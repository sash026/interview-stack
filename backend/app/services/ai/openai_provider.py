import logging

from openai import OpenAI, OpenAIError

from app.core.config import settings
from app.models.insight import PainPointCategory
from app.schemas.insight import InsightsExtraction
from app.services.ai.base import AIProvider
from app.services.exceptions import EmbeddingGenerationError, InsightExtractionError

logger = logging.getLogger(__name__)

_ALLOWED_PAIN_POINT_CATEGORIES = ", ".join(c.value for c in PainPointCategory)

_SYSTEM_PROMPT = f"""You are an analyst extracting structured insights from a customer interview transcript.

Extract exactly the following fields:
- summary: a concise 2-4 sentence summary of the interview.
- pain_points: a list of problems the customer described. Each pain point must have:
  - category: exactly one of [{_ALLOWED_PAIN_POINT_CATEGORIES}]. Never invent a category outside
    this list - pick the closest fit.
  - description: a specific, concrete description of the pain point, grounded in what was actually said.
- feature_requests: features the customer explicitly asked for or implied they want.
- competitors: any competitor products/companies the customer mentioned.
- customer_sentiment: the customer's overall sentiment - positive, neutral, negative, or mixed.
- customer_type: a short label for what kind of customer this is (e.g. "enterprise", "smb", "individual"),
  based only on what the transcript actually indicates.
- action_items: concrete follow-up actions implied by the conversation.
- notable_quotes: short, verbatim quotes from the transcript that are particularly telling.

Only include items that are actually supported by the transcript. Use empty lists rather than inventing
content when a field doesn't apply. Do not include any text outside the structured fields."""


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise InsightExtractionError(
                "OPENAI_API_KEY is not configured; cannot use the openai AI provider."
            )
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_insights(self, transcript: str) -> dict:
        logger.info("Calling OpenAI (%s) to extract insights", settings.OPENAI_MODEL)
        try:
            response = self._client.responses.parse(
                model=settings.OPENAI_MODEL,
                instructions=_SYSTEM_PROMPT,
                input=f"Interview transcript:\n\n{transcript}",
                text_format=InsightsExtraction,
            )
        except OpenAIError as exc:
            raise InsightExtractionError(f"OpenAI request failed: {exc}") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise InsightExtractionError("OpenAI did not return parseable structured output.")
        return parsed.model_dump(mode="json")

    def generate_embedding(self, text: str) -> list[float]:
        try:
            response = self._client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text,
            )
        except OpenAIError as exc:
            raise EmbeddingGenerationError(f"OpenAI embedding request failed: {exc}") from exc
        return response.data[0].embedding
