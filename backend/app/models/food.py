from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_name = Column(String(200), nullable=False)
    meal_category = Column(String(50), default="snack", nullable=False, index=True)  # breakfast, lunch, dinner, snack
    serving_quantity = Column(Float, default=1.0, nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0.0, nullable=False)
    carbs_g = Column(Float, default=0.0, nullable=False)
    fat_g = Column(Float, default=0.0, nullable=False)
    consumed_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    data_source = Column(String(50), default="manual", nullable=False)  # manual, usda, openfoodfacts

    user = relationship("User", back_populates="food_entries")
