from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    weights = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("DailyActivity", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    water_entries = relationship("WaterEntry", back_populates="user", cascade="all, delete-orphan")
    sleep_entries = relationship("SleepEntry", back_populates="user", cascade="all, delete-orphan")
    food_entries = relationship("FoodEntry", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    height_cm = Column(Float, nullable=True)
    preferred_units = Column(String(20), default="metric", nullable=False)  # 'metric' or 'imperial'
    time_zone = Column(String(50), default="UTC", nullable=False)
    fitness_goal = Column(String(50), default="maintain", nullable=False)  # 'lose_weight', 'build_muscle', 'maintain', etc.
    target_weight = Column(Float, nullable=True)
    daily_step_target = Column(Integer, default=10000, nullable=False)
    daily_water_target = Column(Integer, default=2500, nullable=False)  # ml
    daily_sleep_target = Column(Float, default=8.0, nullable=False)  # hours

    user = relationship("User", back_populates="profile")
