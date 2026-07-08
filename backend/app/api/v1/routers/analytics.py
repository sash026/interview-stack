import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import TrendsResponse
from app.services import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> TrendsResponse:
    return analytics_service.get_trends(db, days=days)
