import logging
import uuid

from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import Session

from app.models.embedding import Embedding
from app.models.interview import Interview, InterviewStatus
from app.schemas.embedding import SemanticSearchResult
from app.services import ai_service
from app.services.exceptions import EmbeddingNotFoundError

logger = logging.getLogger(__name__)


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for text via the configured AI provider.

    This is the only place outside app.services.ai_service that knows
    embeddings come from an AIProvider - the worker and the search routes
    only ever call into EmbeddingService, never ai_service directly.
    """
    return ai_service.generate_embedding(text)


def store_embedding(db: Session, interview: Interview, vector: list[float]) -> Embedding:
    """Persist an embedding for an interview, creating the row or updating
    it in place if one already exists (e.g. a retry re-running the
    pipeline for the same interview)."""
    if interview.embedding is not None:
        interview.embedding.vector = vector
        embedding = interview.embedding
    else:
        embedding = Embedding(vector=vector)
        interview.embedding = embedding

    db.commit()
    logger.info("Embedding stored: interview=%s", interview.id)
    return embedding


def semantic_search(db: Session, query: str, limit: int = 10) -> list[SemanticSearchResult]:
    """Rank completed interviews by similarity to a natural-language query,
    e.g. "customers complaining about pricing"."""
    query_vector = generate_embedding(query)
    return _ranked_results(
        db,
        distance_expr=Embedding.vector.cosine_distance(query_vector),
        exclude_interview_id=None,
        limit=limit,
    )


def similar_interviews(
    db: Session, interview_id: uuid.UUID, limit: int = 5
) -> list[SemanticSearchResult]:
    """Rank other completed interviews by similarity to a given interview's
    own transcript embedding."""
    source = db.execute(
        select(Embedding).where(Embedding.interview_id == interview_id)
    ).scalar_one_or_none()
    if source is None:
        raise EmbeddingNotFoundError(
            f"Interview {interview_id} has no embedding yet "
            "(not completed, or still processing)."
        )

    return _ranked_results(
        db,
        distance_expr=Embedding.vector.cosine_distance(source.vector),
        exclude_interview_id=interview_id,
        limit=limit,
    )


def _ranked_results(
    db: Session,
    distance_expr: ColumnElement[float],
    exclude_interview_id: uuid.UUID | None,
    limit: int,
) -> list[SemanticSearchResult]:
    stmt = (
        select(Interview, distance_expr.label("distance"))
        .join(Embedding, Embedding.interview_id == Interview.id)
        .where(Interview.status == InterviewStatus.COMPLETED)
        .order_by(distance_expr)
        .limit(limit)
    )
    if exclude_interview_id is not None:
        stmt = stmt.where(Interview.id != exclude_interview_id)

    rows = db.execute(stmt).all()
    return [
        SemanticSearchResult(
            interview_id=str(interview.id),
            title=interview.title,
            summary=interview.insight.summary if interview.insight is not None else None,
            similarity=1.0 - distance,
        )
        for interview, distance in rows
    ]
