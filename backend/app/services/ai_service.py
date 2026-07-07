import logging

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.insight import InsightsExtraction
from app.services.ai.base import AIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.exceptions import InsightExtractionError

logger = logging.getLogger(__name__)

_PROVIDERS: dict[str, type[AIProvider]] = {
    "mock": MockAIProvider,
    "openai": OpenAIProvider,
}


def _get_provider() -> AIProvider:
    provider_cls = _PROVIDERS.get(settings.AI_PROVIDER)
    if provider_cls is None:
        raise InsightExtractionError(
            f"Unknown AI_PROVIDER: {settings.AI_PROVIDER!r}. "
            f"Available providers: {', '.join(_PROVIDERS)}"
        )
    return provider_cls()


def extract_insights(transcript: str) -> InsightsExtraction:
    """Extract structured insights from a transcript using the configured
    AI provider, validating the provider's raw output against
    InsightsExtraction before returning it. This validation step is what
    guarantees callers only ever see well-formed, taxonomy-conformant data,
    regardless of which provider produced it."""
    provider = _get_provider()
    raw = provider.extract_insights(transcript)
    try:
        return InsightsExtraction.model_validate(raw)
    except ValidationError as exc:
        raise InsightExtractionError(f"AI response failed validation: {exc}") from exc


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for text using the configured AI provider.

    Extension point: not called anywhere in the processing pipeline yet.
    Once embeddings are needed, call this from processing_service after
    insights are saved and persist the result (e.g. via pgvector).
    """
    provider = _get_provider()
    return provider.generate_embedding(text)
