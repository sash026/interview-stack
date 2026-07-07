import logging

from app.models.insight import CustomerSentiment, PainPointCategory
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)

_MOCK_EMBEDDING_DIMENSIONS = 8


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
        return [0.0] * _MOCK_EMBEDDING_DIMENSIONS
