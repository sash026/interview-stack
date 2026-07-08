import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import DashboardMetricsResponse
from app.services import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    top_pain_points_limit: int = Query(default=8, ge=1, le=20),
    top_competitors_limit: int = Query(default=8, ge=1, le=20),
    recent_limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> DashboardMetricsResponse:
    return analytics_service.get_dashboard_metrics(
        db,
        top_pain_points_limit=top_pain_points_limit,
        top_competitors_limit=top_competitors_limit,
        recent_limit=recent_limit,
    )
