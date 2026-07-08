import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.insight import CustomerSentiment, Insight, PainPoint, PainPointCategory
from app.models.interview import Interview, InterviewStatus, Transcript

logger = logging.getLogger(__name__)


def get_interview(db: Session, interview_id: uuid.UUID) -> Interview | None:
    return db.get(Interview, interview_id)


def list_interviews(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status: InterviewStatus | None = None,
    sentiment: CustomerSentiment | None = None,
    pain_point_category: PainPointCategory | None = None,
    customer_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
) -> tuple[list[Interview], int]:
    """Paginated, filterable interview listing for the Interview Explorer.

    Filtering on sentiment/customer_type/pain_point_category requires the
    interview to actually have an Insight (an INNER JOIN), which is correct:
    an interview that hasn't been analyzed yet can't match a sentiment or
    category filter. `q` is a simple title substring match - full-text
    search isn't warranted given semantic search already covers "real"
    search over content.
    """
    stmt = select(Interview)
    needs_insight_join = (
        sentiment is not None or customer_type is not None or pain_point_category is not None
    )

    if needs_insight_join:
        stmt = stmt.join(Insight, Insight.interview_id == Interview.id)
    if pain_point_category is not None:
        stmt = stmt.join(PainPoint, PainPoint.insight_id == Insight.id)

    if status is not None:
        stmt = stmt.where(Interview.status == status)
    if date_from is not None:
        stmt = stmt.where(Interview.created_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(Interview.created_at < date_to + timedelta(days=1))
    if q:
        stmt = stmt.where(Interview.title.ilike(f"%{q}%"))
    if sentiment is not None:
        stmt = stmt.where(Insight.customer_sentiment == sentiment)
    if customer_type:
        stmt = stmt.where(Insight.customer_type.ilike(f"%{customer_type}%"))
    if pain_point_category is not None:
        stmt = stmt.where(PainPoint.category == pain_point_category)

    if pain_point_category is not None:
        stmt = stmt.distinct()

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    stmt = (
        stmt.order_by(Interview.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, total


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
