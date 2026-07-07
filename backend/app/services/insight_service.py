import logging

from sqlalchemy.orm import Session

from app.models.insight import Insight, PainPoint
from app.models.interview import Interview
from app.schemas.insight import InsightsExtraction

logger = logging.getLogger(__name__)


def save_insights(db: Session, interview: Interview, extraction: InsightsExtraction) -> Insight:
    """Persist an InsightsExtraction onto an interview, creating the Insight
    row (and its PainPoint children) or updating it in place if one already
    exists - e.g. a retry re-running extraction for the same interview."""
    pain_points = [
        PainPoint(category=pp.category, description=pp.description)
        for pp in extraction.pain_points
    ]

    if interview.insight is not None:
        insight = interview.insight
        insight.summary = extraction.summary
        insight.feature_requests = extraction.feature_requests
        insight.competitors = extraction.competitors
        insight.customer_sentiment = extraction.customer_sentiment
        insight.customer_type = extraction.customer_type
        insight.action_items = extraction.action_items
        insight.notable_quotes = extraction.notable_quotes
        insight.pain_points.clear()
        insight.pain_points.extend(pain_points)
    else:
        insight = Insight(
            summary=extraction.summary,
            feature_requests=extraction.feature_requests,
            competitors=extraction.competitors,
            customer_sentiment=extraction.customer_sentiment,
            customer_type=extraction.customer_type,
            action_items=extraction.action_items,
            notable_quotes=extraction.notable_quotes,
            pain_points=pain_points,
        )
        interview.insight = insight

    db.commit()
    logger.info(
        "Insights saved: interview=%s pain_points=%d", interview.id, len(pain_points)
    )
    return insight
