from datetime import datetime

from pydantic import BaseModel

from app.schemas.insight import InsightResponse


class InterviewUploadResponse(BaseModel):
    id: str
    title: str
    status: str
    has_audio: bool
    has_notes: bool


class InterviewStatusResponse(BaseModel):
    id: str
    status: str
    failure_reason: str | None = None


class TranscriptResponse(BaseModel):
    raw_text: str | None
    created_at: datetime
    updated_at: datetime


class InterviewDetailResponse(BaseModel):
    id: str
    title: str
    status: str
    input_type: str
    failure_reason: str | None = None
    transcript: TranscriptResponse | None = None
    insights: InsightResponse | None = None
    created_at: datetime
    updated_at: datetime
