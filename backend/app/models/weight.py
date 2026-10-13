from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Date, DateTime, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    measurement_date = Column(Date, nullable=False, index=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "measurement_date", name="uq_user_weight_date"),
    )

    user = relationship("User", back_populates="weights")
