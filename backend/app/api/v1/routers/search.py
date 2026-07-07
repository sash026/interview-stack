import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.embedding import SemanticSearchRequest, SemanticSearchResponse
from app.services import embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchRequest, db: Session = Depends(get_db)
) -> SemanticSearchResponse:
    logger.info("Semantic search: query=%r limit=%d", body.query, body.limit)
    results = embedding_service.semantic_search(db, body.query, limit=body.limit)
    return SemanticSearchResponse(results=results)
