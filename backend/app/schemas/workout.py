from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class WorkoutExerciseBase(BaseModel):
    exercise_name: str = Field(..., min_length=1, max_length=150)
    sets: int = Field(1, ge=1, le=100)
    repetitions: int = Field(0, ge=0, le=1000)
    weight_used: float = Field(0.0, ge=0.0, le=1000.0)
    duration_minutes: Optional[int] = Field(None, ge=0, le=1440)
    distance_km: Optional[float] = Field(None, ge=0.0, le=1000.0)
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseOut(WorkoutExerciseBase):
    id: int
    workout_id: int

    model_config = ConfigDict(from_attributes=True)


class WorkoutBase(BaseModel):
    workout_name: str = Field(..., min_length=1, max_length=150)
    workout_type: str = Field("strength", max_length=50)
    start_time: datetime
    duration_minutes: int = Field(0, ge=0, le=1440)
    notes: Optional[str] = Field(None, max_length=1000)
    estimated_calories: Optional[float] = Field(None, ge=0.0, le=10000.0)


class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate] = []


class WorkoutUpdate(BaseModel):
    workout_name: Optional[str] = Field(None, min_length=1, max_length=150)
    workout_type: Optional[str] = Field(None, max_length=50)
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0, le=1440)
    notes: Optional[str] = Field(None, max_length=1000)
    estimated_calories: Optional[float] = Field(None, ge=0.0, le=10000.0)
    exercises: Optional[List[WorkoutExerciseCreate]] = None


class WorkoutOut(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    exercises: List[WorkoutExerciseOut] = []

    model_config = ConfigDict(from_attributes=True)
