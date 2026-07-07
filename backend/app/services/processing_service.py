import logging
import os
import uuid

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.interview import InputType
from app.services import interview_service, storage, transcription_service
from app.services.exceptions import AudioNotFoundError, TranscriptionError

logger = logging.getLogger(__name__)


def process_interview(interview_id: str) -> None:
    """Orchestrates async processing of a single interview: mark it
    processing, produce a transcript (downloading + transcribing audio, or
    reusing notes as-is), save it, and mark completed. Any failure is
    caught, logged, and persisted as a failure reason on the interview
    rather than left to crash the worker silently.
    """
    db = SessionLocal()
    try:
        interview = interview_service.get_interview(db, uuid.UUID(interview_id))
        if interview is None:
            logger.error("Interview %s not found; nothing to process", interview_id)
            return

        interview_service.mark_processing(db, interview)

        if interview.input_type == InputType.AUDIO:
            if not interview.audio_s3_key:
                raise AudioNotFoundError(
                    f"Interview {interview_id} has input_type=audio but no audio_s3_key"
                )

            logger.info(
                "Downloading audio: interview=%s key=%s",
                interview_id,
                interview.audio_s3_key,
            )
            local_path = storage.download_to_tempfile(interview.audio_s3_key)
            try:
                logger.info("Transcription started: interview=%s", interview_id)
                raw_text = transcription_service.transcribe(local_path)
                logger.info("Transcription completed: interview=%s", interview_id)
            finally:
                os.remove(local_path)
        else:
            raw_text = interview.raw_notes_text or ""

        interview_service.save_transcript(db, interview, raw_text)
        interview_service.mark_completed(db, interview)

        # Extension point: AI extraction / embedding generation will run
        # here once implemented, triggered off the freshly saved transcript.

    except (AudioNotFoundError, TranscriptionError) as exc:
        logger.error("Processing failed for interview %s: %s", interview_id, exc)
        _mark_failed_safely(db, interview_id, str(exc))
        raise
    except Exception as exc:
        logger.exception("Unexpected error processing interview %s", interview_id)
        _mark_failed_safely(db, interview_id, f"Unexpected error: {exc}")
        raise
    finally:
        db.close()


def _mark_failed_safely(db: Session, interview_id: str, reason: str) -> None:
    """Marks an interview failed on a rolled-back session. Used from
    exception handlers, where the session may hold a failed transaction
    from whatever step just raised. Swallows its own failures (e.g. the
    database being the thing that's down) so the original error is what
    propagates, not a secondary one from this cleanup step."""
    try:
        db.rollback()
        interview = interview_service.get_interview(db, uuid.UUID(interview_id))
        if interview is not None:
            interview_service.mark_failed(db, interview, reason)
    except Exception:
        logger.exception(
            "Could not persist failed status for interview %s (original error: %s)",
            interview_id,
            reason,
        )
