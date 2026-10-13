from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_name = Column(String(150), nullable=False)
    workout_type = Column(String(50), default="strength", nullable=False, index=True)  # strength, cardio, hiit, yoga, walking, cycling, other
    start_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=0, nullable=False)
    notes = Column(String(1000), nullable=True)
    estimated_calories = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_name = Column(String(150), nullable=False)
    sets = Column(Integer, default=1, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    weight_used = Column(Float, default=0.0, nullable=False)  # in kg
    duration_minutes = Column(Integer, nullable=True)
    distance_km = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)

    workout = relationship("Workout", back_populates="exercises")
