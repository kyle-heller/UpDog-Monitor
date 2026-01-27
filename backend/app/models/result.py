# [SQLAlchemy] - CheckResult model
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def utc_now():
    return datetime.utcnow()


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("monitors.id"))
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_up: Mapped[bool] = mapped_column(Boolean)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # [SQLAlchemy] - Relationship to Monitor
    monitor: Mapped["Monitor"] = relationship(back_populates="check_results")
