import hashlib
import logging
import math

from app.core.config import settings
from app.models.insight import CustomerSentiment, PainPointCategory
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


class MockAIProvider(AIProvider):
    """Stand-in AI backend used until a real provider (OpenAI, Anthropic,
    Gemini, ...) is configured. Returns deterministic, schema-conformant
    output derived from the transcript so the extraction/validation/
    persistence plumbing can be exercised end-to-end without an API key."""

    def extract_insights(self, transcript: str) -> dict:
        snippet = transcript.strip()[:200] or "(empty transcript)"
        logger.info("Mock-extracting insights from transcript (%d chars)", len(transcript))
        return {
            "summary": f"[Mock summary] {snippet}",
            "pain_points": [
                {
                    "category": PainPointCategory.ONBOARDING.value,
                    "description": "[Mock] No real AI provider configured yet.",
                }
            ],
            "feature_requests": [],
            "competitors": [],
            "customer_sentiment": CustomerSentiment.NEUTRAL.value,
            "customer_type": "unknown",
            "action_items": [],
            "notable_quotes": [],
        }

    def generate_embedding(self, text: str) -> list[float]:
        logger.info("Mock-generating embedding for text (%d chars)", len(text))
        return _deterministic_unit_vector(text, settings.EMBEDDING_DIMENSIONS)


def _deterministic_unit_vector(text: str, dimensions: int) -> list[float]:
    """Derive a stable, non-zero unit vector from text via hashing. This is
    not a real embedding - it carries no semantic meaning - but it lets
    pgvector cosine-distance queries run correctly end-to-end without an
    AI provider (a real all-zero vector, which a naive mock might return,
    is invalid for cosine distance: the norm is zero)."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    repeated = (digest * ((dimensions // len(digest)) + 1))[:dimensions]
    raw = [(byte - 128) / 128 for byte in repeated]
    norm = math.sqrt(sum(value * value for value in raw)) or 1.0
    return [value / norm for value in raw]
