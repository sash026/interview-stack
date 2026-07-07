from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class SemanticSearchResult(BaseModel):
    interview_id: str
    title: str
    summary: str | None = None
    similarity: float


class SemanticSearchResponse(BaseModel):
    results: list[SemanticSearchResult]


class SimilarInterviewsResponse(BaseModel):
    results: list[SemanticSearchResult]
