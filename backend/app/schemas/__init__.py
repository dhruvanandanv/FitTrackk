from backend.app.schemas.auth import UserRegister, UserLogin, UserOut, TokenResponse
from backend.app.schemas.user import UserProfileBase, UserProfileUpdate, UserProfileOut, UserProfileWithDetails
from backend.app.schemas.weight import WeightCreate, WeightUpdate, WeightOut
from backend.app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityOut
from backend.app.schemas.workout import (
    WorkoutCreate, WorkoutUpdate, WorkoutOut,
    WorkoutExerciseCreate, WorkoutExerciseOut
)
from backend.app.schemas.water import WaterCreate, WaterOut, WaterDaySummary
from backend.app.schemas.sleep import SleepCreate, SleepUpdate, SleepOut
from backend.app.schemas.food import FoodCreate, FoodUpdate, FoodOut, FoodDaySummary
from backend.app.schemas.dashboard import TodaySummary, MetricProgress
from backend.app.schemas.analytics import (
    WeeklyAnalyticsResponse, MonthlyAnalyticsResponse,
    WeightAnalyticsResponse, WorkoutAnalyticsResponse
)

__all__ = [
    "UserRegister", "UserLogin", "UserOut", "TokenResponse",
    "UserProfileBase", "UserProfileUpdate", "UserProfileOut", "UserProfileWithDetails",
    "WeightCreate", "WeightUpdate", "WeightOut",
    "ActivityCreate", "ActivityUpdate", "ActivityOut",
    "WorkoutCreate", "WorkoutUpdate", "WorkoutOut",
    "WorkoutExerciseCreate", "WorkoutExerciseOut",
    "WaterCreate", "WaterOut", "WaterDaySummary",
    "SleepCreate", "SleepUpdate", "SleepOut",
    "FoodCreate", "FoodUpdate", "FoodOut", "FoodDaySummary",
    "TodaySummary", "MetricProgress",
    "WeeklyAnalyticsResponse", "MonthlyAnalyticsResponse",
    "WeightAnalyticsResponse", "WorkoutAnalyticsResponse",
]
