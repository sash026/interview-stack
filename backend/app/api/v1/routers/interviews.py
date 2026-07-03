import logging
import uuid

from fastapi import APIRouter, Form, HTTPException, UploadFile, status

from app.schemas.interview import InterviewUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

ALLOWED_AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")


@router.post("/upload", response_model=InterviewUploadResponse)
async def upload_interview(
    title: str = Form(...),
    audio_file: UploadFile | None = None,
    notes: str | None = Form(None),
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

    if has_audio and not audio_file.filename.lower().endswith(ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported audio file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    interview_id = str(uuid.uuid4())

    if has_audio:
        audio_bytes = await audio_file.read()
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

    # TODO: persist to PostgreSQL, upload audio to S3, and enqueue a
    # Celery task for transcription/processing. Mocked for now.
    return InterviewUploadResponse(
        id=interview_id,
        title=title,
        status="received",
        has_audio=has_audio,
        has_notes=has_notes,
    )
