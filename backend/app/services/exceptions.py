class AudioNotFoundError(Exception):
    """Raised when an interview's audio object is missing from S3."""


class TranscriptionError(Exception):
    """Raised when a TranscriptionProvider fails to produce a transcript."""


class InsightExtractionError(Exception):
    """Raised when an AIProvider fails to produce insights, or its output
    fails validation against the expected structured schema."""


class EmbeddingGenerationError(Exception):
    """Raised when an AIProvider fails to produce or persist an embedding."""


class EmbeddingNotFoundError(Exception):
    """Raised when similar_interviews is asked about an interview that has
    no stored embedding yet (still processing, failed, or not completed)."""
