from abc import ABC, abstractmethod


class AIProvider(ABC):
    """An LLM backend used for interview intelligence. Business logic must
    never call an LLM SDK (OpenAI, Anthropic, Gemini, ...) directly - it
    goes through an AIProvider implementation, selected and orchestrated by
    app.services.ai_service.

    Implementations return plain dicts/lists rather than validated Pydantic
    models: app.services.ai_service is solely responsible for validating a
    provider's raw output against the expected schema, so that guarantee
    holds uniformly across every provider, not just ones with SDK-level
    structured-output support.
    """

    @abstractmethod
    def extract_insights(self, transcript: str) -> dict:
        """Return a raw dict matching the InsightsExtraction schema shape."""
        raise NotImplementedError

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Return an embedding vector for text. Not yet wired into the
        processing pipeline - this is the extension point for it."""
        raise NotImplementedError
