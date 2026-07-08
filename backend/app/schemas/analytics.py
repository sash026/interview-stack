from datetime import date, datetime

from pydantic import BaseModel


class PainPointCount(BaseModel):
    category: str
    count: int


class CompetitorCount(BaseModel):
    name: str
    count: int


class SentimentCount(BaseModel):
    sentiment: str
    count: int
    percentage: float


class RecentInterviewItem(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    sentiment: str | None = None
    summary_preview: str | None = None


class DashboardMetricsResponse(BaseModel):
    total_interviews: int
    top_pain_points: list[PainPointCount]
    sentiment_breakdown: list[SentimentCount]
    top_competitors: list[CompetitorCount]
    recent_interviews: list[RecentInterviewItem]


class PainPointTrendPoint(BaseModel):
    date: date
    category: str
    count: int


class SentimentTrendPoint(BaseModel):
    date: date
    sentiment: str
    count: int


class CategoryBreakdownItem(BaseModel):
    category: str
    count: int


class TrendsResponse(BaseModel):
    days: int
    pain_point_trends: list[PainPointTrendPoint]
    sentiment_trends: list[SentimentTrendPoint]
    category_breakdown: list[CategoryBreakdownItem]
