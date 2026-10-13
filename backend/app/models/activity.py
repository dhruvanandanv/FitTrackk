from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Date, DateTime, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class DailyActivity(Base):
    __tablename__ = "daily_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False, index=True)
    steps = Column(Integer, default=0, nullable=False)
    active_minutes = Column(Integer, default=0, nullable=False)
    cardio_minutes = Column(Integer, default=0, nullable=False)
    calories_burned = Column(Float, nullable=True)
    data_source = Column(String(50), default="manual", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "activity_date", name="uq_user_activity_date"),
    )

    user = relationship("User", back_populates="activities")
