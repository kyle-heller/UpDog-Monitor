# [SQLAlchemy] - Monitor model
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy import Boolean, DateTime, Integer, String

from app.models import Base


def utc_now():
    return datetime.now(timezone.utc)


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )
    # [SQLAlchemy] - Relationship to CheckResults
    check_results: Mapped[list["CheckResult"]] = relationship(back_populates="monitor")
