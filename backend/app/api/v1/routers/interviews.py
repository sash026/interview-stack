import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.db.session import get_db
from app.models.interview import InputType, Interview, InterviewStatus
from app.schemas.interview import InterviewUploadResponse
from app.services import storage
from app.tasks.transcription import transcribe_interview_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

ALLOWED_AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")


@router.post("/upload", response_model=InterviewUploadResponse)
async def upload_interview(
    title: str = Form(...),
    audio_file: UploadFile | None = None,
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
) -> InterviewUploadResponse:
    has_audio = audio_file is not None
    has_notes = bool(notes and notes.strip())

    if not has_audio and not has_notes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either an audio file or text notes.",
        )

    if has_audio and has_notes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide only one: an audio file or text notes, not both.",
        )

    if (
        has_audio
        and audio_file is not None
        and not (audio_file.filename or "").lower().endswith(ALLOWED_AUDIO_EXTENSIONS)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported audio file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    interview_id = uuid.uuid4()
    audio_s3_key: str | None = None
    audio_url: str | None = None

    if audio_file is not None:
        audio_bytes = await audio_file.read()
        audio_s3_key = f"interviews/{interview_id}/{audio_file.filename}"

        if settings.AWS_ACCESS_KEY_ID:
            await run_in_threadpool(
                storage.upload_file,
                BytesIO(audio_bytes),
                audio_s3_key,
                audio_file.content_type,
            )
            audio_url = await run_in_threadpool(
                storage.generate_presigned_view_url, audio_s3_key
            )
        else:
            logger.warning(
                "AWS credentials not configured; mocking S3 upload for key=%s",
                audio_s3_key,
            )

        logger.info(
            "Received interview upload: id=%s title=%r filename=%r "
            "content_type=%r size_bytes=%d",
            interview_id,
            title,
            audio_file.filename,
            audio_file.content_type,
            len(audio_bytes),
        )
    else:
        logger.info(
            "Received interview upload: id=%s title=%r notes_length=%d",
            interview_id,
            title,
            len(notes or ""),
        )

    interview = Interview(
        id=interview_id,
        title=title,
        status=InterviewStatus.PENDING,
        input_type=InputType.AUDIO if has_audio else InputType.NOTES,
        raw_notes_text=notes if has_notes else None,
        audio_s3_key=audio_s3_key,
        audio_url=audio_url,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    transcribe_interview_task.delay(str(interview.id))

    return InterviewUploadResponse(
        id=str(interview.id),
        title=interview.title,
        status=interview.status.value,
        has_audio=has_audio,
        has_notes=has_notes,
    )
