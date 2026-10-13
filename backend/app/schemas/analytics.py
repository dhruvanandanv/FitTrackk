from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.weight import WeightOut


class DayMetric(BaseModel):
    date: date
    steps: int
    active_minutes: int
    water_ml: int
    sleep_minutes: int
    calories_consumed: float
    calories_burned: float
    workout_minutes: int


class WeeklyAnalyticsResponse(BaseModel):
    start_date: date
    end_date: date
    total_steps: int
    avg_daily_steps: int
    total_workouts: int
    total_workout_minutes: int
    total_water_ml: int
    avg_sleep_hours: float
    total_calories_consumed: float
    total_calories_burned: float
    goal_completion_rate: float
    days: List[DayMetric]


class MonthlyAnalyticsResponse(BaseModel):
    start_date: date
    end_date: date
    total_steps: int
    avg_daily_steps: int
    total_workouts: int
    total_workout_minutes: int
    total_calories_consumed: float
    days: List[DayMetric]


class WeightAnalyticsResponse(BaseModel):
    latest_weight: Optional[float] = None
    earliest_weight: Optional[float] = None
    weight_change: Optional[float] = None
    target_weight: Optional[float] = None
    progress_percentage: Optional[float] = None
    goal_type: str = "maintain"
    history: List[WeightOut] = []


class WorkoutAnalyticsResponse(BaseModel):
    total_workouts: int
    total_duration_minutes: int
    by_type: Dict[str, int]
    recent_exercises: List[str]
