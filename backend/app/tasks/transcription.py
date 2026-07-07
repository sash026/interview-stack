import logging

from sqlalchemy.exc import OperationalError

from app.core.celery_app import celery_app
from app.services.processing_service import process_interview

logger = logging.getLogger(__name__)


@celery_app.task(
    name="transcribe_interview",
    bind=True,
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,
)
def transcribe_interview_task(self, interview_id: str) -> None:
    logger.info("Worker started: interview=%s task_id=%s", interview_id, self.request.id)
    try:
        process_interview(interview_id)
    except Exception:
        logger.error("Worker failed: interview=%s task_id=%s", interview_id, self.request.id)
        raise
    else:
        logger.info("Worker finished: interview=%s task_id=%s", interview_id, self.request.id)
