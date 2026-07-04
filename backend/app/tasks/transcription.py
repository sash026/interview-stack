import logging
import uuid

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.interview import InputType, Interview, InterviewStatus, Transcript
from app.services.transcription import transcribe_audio

logger = logging.getLogger(__name__)


@celery_app.task(name="transcribe_interview", bind=True)
def transcribe_interview_task(self, interview_id: str) -> None:
    db = SessionLocal()
    try:
        interview = db.get(Interview, uuid.UUID(interview_id))
        if interview is None:
            logger.error("Interview %s not found; skipping transcription", interview_id)
            return

        interview.status = InterviewStatus.TRANSCRIBING
        db.commit()

        if interview.input_type == InputType.AUDIO:
            raw_text = transcribe_audio(interview.audio_s3_key or "")
        else:
            raw_text = interview.raw_notes_text or ""

        interview.status = InterviewStatus.PROCESSING
        db.commit()

        if interview.transcript is not None:
            interview.transcript.raw_text = raw_text
        else:
            interview.transcript = Transcript(raw_text=raw_text)

        interview.status = InterviewStatus.COMPLETED
        db.commit()
        logger.info("Completed transcription for interview %s", interview_id)
    except Exception:
        db.rollback()
        interview = db.get(Interview, uuid.UUID(interview_id))
        if interview is not None:
            interview.status = InterviewStatus.FAILED
            db.commit()
        logger.exception("Transcription failed for interview %s", interview_id)
        raise
    finally:
        db.close()
