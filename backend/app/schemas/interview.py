from pydantic import BaseModel


class InterviewUploadResponse(BaseModel):
    id: str
    title: str
    status: str
    has_audio: bool
    has_notes: bool
