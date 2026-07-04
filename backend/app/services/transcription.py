import logging

logger = logging.getLogger(__name__)

_MOCK_TRANSCRIPT_TEXT = (
    "[Mock transcript] Speech-to-text is not wired up to a real provider "
    "yet; this placeholder stands in for the eventual Whisper/AWS "
    "Transcribe output."
)


def transcribe_audio(audio_s3_key: str) -> str:
    """Transcribe an audio file stored in S3, returning the raw text.

    Mocked for now since no speech-to-text provider is configured; swap
    this out for a real Whisper/AWS Transcribe call once one is chosen.
    """
    logger.info("Mock-transcribing audio at s3_key=%s", audio_s3_key)
    return _MOCK_TRANSCRIPT_TEXT
