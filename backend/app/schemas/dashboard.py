from datetime import date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from backend.app.schemas.workout import WorkoutOut


class MetricProgress(BaseModel):
    current: float
    target: float
    percentage: float  # capped at 100 for visual rings, but actual retained
    actual_percentage: float
    unit: str


class TodaySummary(BaseModel):
    date: date
    greeting: str
    user_name: str
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    weight_change: Optional[float] = None
    bmi: Optional[float] = None  # Optional screening metric
    steps: MetricProgress
    water: MetricProgress
    sleep: MetricProgress
    calories_consumed: float
    calories_burned: float
    workouts_count: int
    workouts_duration_minutes: int
    recent_workouts: List[WorkoutOut] = []
    weekly_activity_trend: List[Dict[str, Any]] = []
    weight_trend: List[Dict[str, Any]] = []
