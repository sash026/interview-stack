import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.insight import CustomerSentiment, Insight, PainPoint, PainPointCategory
from app.models.interview import Interview, InterviewStatus
from app.schemas.analytics import (
    CategoryBreakdownItem,
    CompetitorCount,
    DashboardMetricsResponse,
    PainPointCount,
    PainPointTrendPoint,
    RecentInterviewItem,
    SentimentCount,
    SentimentTrendPoint,
    TrendsResponse,
)

logger = logging.getLogger(__name__)

_SUMMARY_PREVIEW_LENGTH = 160


def _summary_preview(summary: str | None) -> str | None:
    if not summary:
        return None
    if len(summary) <= _SUMMARY_PREVIEW_LENGTH:
        return summary
    return summary[:_SUMMARY_PREVIEW_LENGTH] + "..."


def _pain_point_counts(db: Session, since: datetime | None = None) -> list[tuple[str, int]]:
    stmt = (
        select(PainPoint.category, func.count().label("count"))
        .select_from(PainPoint)
        .join(Insight, PainPoint.insight_id == Insight.id)
        .join(Interview, Insight.interview_id == Interview.id)
        .where(Interview.status == InterviewStatus.COMPLETED)
        .group_by(PainPoint.category)
        .order_by(func.count().desc())
    )
    if since is not None:
        stmt = stmt.where(Interview.created_at >= since)
    rows = db.execute(stmt).all()
    return [(category.value, count) for category, count in rows]


def _sentiment_counts(db: Session) -> dict[str, int]:
    stmt = (
        select(Insight.customer_sentiment, func.count().label("count"))
        .select_from(Insight)
        .join(Interview, Insight.interview_id == Interview.id)
        .where(Interview.status == InterviewStatus.COMPLETED)
        .group_by(Insight.customer_sentiment)
    )
    rows = db.execute(stmt).all()
    return {sentiment.value: count for sentiment, count in rows}


def _competitor_counts(db: Session, limit: int) -> list[tuple[str, int]]:
    # jsonb_array_elements_text + grouping by normalized casing doesn't map
    # cleanly onto the ORM's expression language, so this one query is raw
    # SQL (still executed through the SQLAlchemy engine, still parameterized).
    stmt = text(
        """
        SELECT
            (array_agg(competitor.value ORDER BY competitor.value))[1] AS display_name,
            COUNT(*) AS mentions
        FROM insights
        JOIN interviews ON interviews.id = insights.interview_id
        CROSS JOIN LATERAL jsonb_array_elements_text(insights.competitors) AS competitor(value)
        WHERE interviews.status = :status AND competitor.value <> ''
        GROUP BY lower(trim(competitor.value))
        ORDER BY mentions DESC
        LIMIT :limit
        """
    )
    rows = db.execute(stmt, {"status": InterviewStatus.COMPLETED.value, "limit": limit}).all()
    return [(row.display_name, row.mentions) for row in rows]


def _to_recent_item(interview: Interview) -> RecentInterviewItem:
    insight = interview.insight
    return RecentInterviewItem(
        id=str(interview.id),
        title=interview.title,
        status=interview.status.value,
        created_at=interview.created_at,
        sentiment=insight.customer_sentiment.value if insight is not None else None,
        summary_preview=_summary_preview(insight.summary) if insight is not None else None,
    )


def get_dashboard_metrics(
    db: Session,
    *,
    top_pain_points_limit: int = 8,
    top_competitors_limit: int = 8,
    recent_limit: int = 10,
) -> DashboardMetricsResponse:
    """Aggregates across every completed interview: this is the whole-corpus
    snapshot shown on the dashboard homepage (as opposed to /analytics/trends,
    which is windowed by time)."""
    total_interviews = db.execute(
        select(func.count())
        .select_from(Interview)
        .where(Interview.status == InterviewStatus.COMPLETED)
    ).scalar_one()

    pain_point_counts = _pain_point_counts(db)[:top_pain_points_limit]

    sentiment_counts = _sentiment_counts(db)
    sentiment_total = sum(sentiment_counts.values()) or 1
    sentiment_breakdown = [
        SentimentCount(
            sentiment=sentiment.value,
            count=sentiment_counts.get(sentiment.value, 0),
            percentage=round(sentiment_counts.get(sentiment.value, 0) / sentiment_total * 100, 1),
        )
        for sentiment in CustomerSentiment
    ]

    competitor_counts = _competitor_counts(db, top_competitors_limit)

    recent_stmt = select(Interview).order_by(Interview.created_at.desc()).limit(recent_limit)
    recent_interviews = list(db.execute(recent_stmt).scalars().all())

    return DashboardMetricsResponse(
        total_interviews=total_interviews,
        top_pain_points=[PainPointCount(category=c, count=n) for c, n in pain_point_counts],
        sentiment_breakdown=sentiment_breakdown,
        top_competitors=[CompetitorCount(name=name, count=n) for name, n in competitor_counts],
        recent_interviews=[_to_recent_item(interview) for interview in recent_interviews],
    )


def get_trends(db: Session, *, days: int = 30) -> TrendsResponse:
    """Time-windowed view of the same underlying data as the dashboard,
    bucketed by day, for "is this getting better or worse" questions."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    pain_stmt = (
        select(
            func.date_trunc("day", Interview.created_at).label("day"),
            PainPoint.category,
            func.count().label("count"),
        )
        .select_from(PainPoint)
        .join(Insight, PainPoint.insight_id == Insight.id)
        .join(Interview, Insight.interview_id == Interview.id)
        .where(Interview.status == InterviewStatus.COMPLETED, Interview.created_at >= since)
        .group_by("day", PainPoint.category)
        .order_by("day")
    )
    pain_rows = db.execute(pain_stmt).all()

    sentiment_stmt = (
        select(
            func.date_trunc("day", Interview.created_at).label("day"),
            Insight.customer_sentiment,
            func.count().label("count"),
        )
        .select_from(Insight)
        .join(Interview, Insight.interview_id == Interview.id)
        .where(Interview.status == InterviewStatus.COMPLETED, Interview.created_at >= since)
        .group_by("day", Insight.customer_sentiment)
        .order_by("day")
    )
    sentiment_rows = db.execute(sentiment_stmt).all()

    category_totals: dict[str, int] = {category.value: 0 for category in PainPointCategory}
    for _, category, count in pain_rows:
        category_totals[category.value] += count

    return TrendsResponse(
        days=days,
        pain_point_trends=[
            PainPointTrendPoint(date=day.date(), category=category.value, count=count)
            for day, category, count in pain_rows
        ],
        sentiment_trends=[
            SentimentTrendPoint(date=day.date(), sentiment=sentiment.value, count=count)
            for day, sentiment, count in sentiment_rows
        ],
        category_breakdown=sorted(
            (CategoryBreakdownItem(category=category, count=count) for category, count in category_totals.items()),
            key=lambda item: -item.count,
        ),
    )
