from datetime import datetime

from pydantic import BaseModel, Field

from app.models.insight import CustomerSentiment, PainPointCategory


class PainPointExtraction(BaseModel):
    category: PainPointCategory
    description: str = Field(..., min_length=1)


class InsightsExtraction(BaseModel):
    """The contract every AI provider's raw output must validate against
    before it's persisted. This is also handed to OpenAI as the structured
    output schema, so the shape the model is asked to produce and the shape
    we validate on the way back are guaranteed to be the same type."""

    summary: str = Field(..., min_length=1)
    pain_points: list[PainPointExtraction]
    feature_requests: list[str]
    competitors: list[str]
    customer_sentiment: CustomerSentiment
    customer_type: str = Field(..., min_length=1)
    action_items: list[str]
    notable_quotes: list[str]


class PainPointResponse(BaseModel):
    category: str
    description: str


class InsightResponse(BaseModel):
    summary: str
    pain_points: list[PainPointResponse]
    feature_requests: list[str]
    competitors: list[str]
    customer_sentiment: str
    customer_type: str
    action_items: list[str]
    notable_quotes: list[str]
    created_at: datetime
    updated_at: datetime
