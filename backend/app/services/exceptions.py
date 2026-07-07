class AudioNotFoundError(Exception):
    """Raised when an interview's audio object is missing from S3."""


class TranscriptionError(Exception):
    """Raised when a TranscriptionProvider fails to produce a transcript."""


class InsightExtractionError(Exception):
    """Raised when an AIProvider fails to produce insights, or its output
    fails validation against the expected structured schema."""
