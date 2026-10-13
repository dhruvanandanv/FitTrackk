from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class SleepEntry(Base):
    __tablename__ = "sleep_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sleep_start = Column(DateTime, nullable=False, index=True)
    sleep_end = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # calculated minutes
    quality_rating = Column(Integer, nullable=True)  # 1 to 5 scale
    data_source = Column(String(50), default="manual", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="sleep_entries")
