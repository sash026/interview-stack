from abc import ABC, abstractmethod


class TranscriptionProvider(ABC):
    """A speech-to-text backend. Implementations receive a local file path
    (the caller is responsible for downloading the audio first) and return
    the transcribed text."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError
