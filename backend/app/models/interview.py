import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InputType(str, enum.Enum):
    AUDIO = "audio"
    NOTES = "notes"


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(
            InterviewStatus,
            name="interview_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=InterviewStatus.PENDING,
    )
    input_type: Mapped[InputType] = mapped_column(
        Enum(
            InputType,
            name="interview_input_type",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    raw_notes_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_s3_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    transcript: Mapped["Transcript | None"] = relationship(
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Holds a list of {start, end, speaker, text} segments once diarization
    # lands; left flexible/JSONB rather than modeled as columns for now.
    segments: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(back_populates="transcript")
