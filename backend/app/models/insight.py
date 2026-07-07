import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.interview import Interview


class PainPointCategory(str, enum.Enum):
    """Fixed taxonomy the AI must choose from when categorizing a pain
    point. Not an arbitrary/free-form field by design."""

    PRICING = "pricing"
    REPORTING = "reporting"
    AUTHENTICATION = "authentication"
    ONBOARDING = "onboarding"
    INTEGRATIONS = "integrations"
    PERFORMANCE = "performance"
    UX = "ux"
    DOCUMENTATION = "documentation"
    ANALYTICS = "analytics"
    SECURITY = "security"
    COLLABORATION = "collaboration"
    SUPPORT = "support"


class CustomerSentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    feature_requests: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    competitors: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    customer_sentiment: Mapped[CustomerSentiment] = mapped_column(
        Enum(
            CustomerSentiment,
            name="insight_customer_sentiment",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
    )
    customer_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action_items: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    notable_quotes: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    interview: Mapped["Interview"] = relationship(back_populates="insight")
    pain_points: Mapped[list["PainPoint"]] = relationship(
        back_populates="insight",
        cascade="all, delete-orphan",
        order_by="PainPoint.created_at",
    )


class PainPoint(Base):
    __tablename__ = "pain_points"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    insight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("insights.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[PainPointCategory] = mapped_column(
        Enum(
            PainPointCategory,
            name="pain_point_category",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    insight: Mapped["Insight"] = relationship(back_populates="pain_points")
