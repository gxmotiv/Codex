from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def uuid_str() -> str:
    return str(uuid4())


class SavedChart(Base):
    __tablename__ = "saved_charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), index=True)
    birth_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    latitude: Mapped[str] = mapped_column(String(64))
    longitude: Mapped[str] = mapped_column(String(64))
    timezone: Mapped[str] = mapped_column(String(64))
    chart_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    queries: Mapped[list["UserQuery"]] = relationship(back_populates="chart", cascade="all, delete-orphan")


class UserQuery(Base):
    __tablename__ = "user_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    chart_id: Mapped[str | None] = mapped_column(ForeignKey("saved_charts.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    context_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    prediction_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    llm_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    chart: Mapped[SavedChart | None] = relationship(back_populates="queries")


class GoldenValidationChart(Base):
    __tablename__ = "golden_validation_charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    label: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(255))
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    expected_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    tolerance_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
