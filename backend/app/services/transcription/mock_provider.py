import logging
import os

from app.services.exceptions import TranscriptionError
from app.services.transcription.base import TranscriptionProvider

logger = logging.getLogger(__name__)


class MockTranscriptionProvider(TranscriptionProvider):
    """Stand-in speech-to-text backend used until a real provider (e.g.
    OpenAI Whisper) is configured. It reads the downloaded audio file to
    prove the download/transcribe plumbing works end-to-end, then returns
    clearly-labeled placeholder text rather than an actual transcript."""

    def transcribe(self, audio_path: str) -> str:
        try:
            size_bytes = os.path.getsize(audio_path)
        except OSError as exc:
            raise TranscriptionError(
                f"Could not read audio file at {audio_path}: {exc}"
            ) from exc

        logger.info("Mock-transcribing audio file=%s size_bytes=%d", audio_path, size_bytes)
        return (
            "[Mock transcript] Speech-to-text is not wired up to a real "
            "provider yet; this placeholder stands in for the eventual "
            f"Whisper/AWS Transcribe output. (source file: {size_bytes} bytes)"
        )
