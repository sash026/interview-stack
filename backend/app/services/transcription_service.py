import logging

from app.core.config import settings
from app.services.exceptions import TranscriptionError
from app.services.transcription.base import TranscriptionProvider
from app.services.transcription.mock_provider import MockTranscriptionProvider

logger = logging.getLogger(__name__)

_PROVIDERS: dict[str, type[TranscriptionProvider]] = {
    "mock": MockTranscriptionProvider,
}


def _get_provider() -> TranscriptionProvider:
    provider_cls = _PROVIDERS.get(settings.TRANSCRIPTION_PROVIDER)
    if provider_cls is None:
        raise TranscriptionError(
            f"Unknown TRANSCRIPTION_PROVIDER: {settings.TRANSCRIPTION_PROVIDER!r}. "
            f"Available providers: {', '.join(_PROVIDERS)}"
        )
    return provider_cls()


def transcribe(audio_path: str) -> str:
    """Transcribe a local audio file using the configured provider."""
    provider = _get_provider()
    return provider.transcribe(audio_path)
