import logging
import uuid

from sqlalchemy.orm import Session

from app.models.interview import Interview, InterviewStatus, Transcript

logger = logging.getLogger(__name__)


def get_interview(db: Session, interview_id: uuid.UUID) -> Interview | None:
    return db.get(Interview, interview_id)


def mark_processing(db: Session, interview: Interview) -> None:
    interview.status = InterviewStatus.PROCESSING
    interview.failure_reason = None
    db.commit()
    logger.info("Status updated: interview=%s status=%s", interview.id, interview.status.value)


def save_transcript(db: Session, interview: Interview, raw_text: str) -> None:
    if interview.transcript is not None:
        interview.transcript.raw_text = raw_text
    else:
        interview.transcript = Transcript(raw_text=raw_text)
    db.commit()


def mark_completed(db: Session, interview: Interview) -> None:
    interview.status = InterviewStatus.COMPLETED
    db.commit()
    logger.info("Status updated: interview=%s status=%s", interview.id, interview.status.value)


def mark_failed(db: Session, interview: Interview, reason: str) -> None:
    interview.status = InterviewStatus.FAILED
    interview.failure_reason = reason
    db.commit()
    logger.info("Status updated: interview=%s status=%s", interview.id, interview.status.value)


def reset_for_retry(db: Session, interview: Interview) -> None:
    interview.status = InterviewStatus.UPLOADED
    interview.failure_reason = None
    db.commit()
    logger.info("Status updated: interview=%s status=%s", interview.id, interview.status.value)
