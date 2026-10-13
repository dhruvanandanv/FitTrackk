from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.auth import UserOut


class UserProfileBase(BaseModel):
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    preferred_units: str = Field("metric", pattern="^(metric|imperial)$")
    time_zone: str = "UTC"
    fitness_goal: str = "maintain"
    target_weight: Optional[float] = Field(None, ge=20, le=500)
    daily_step_target: int = Field(10000, ge=1000, le=100000)
    daily_water_target: int = Field(2500, ge=500, le=10000)
    daily_sleep_target: float = Field(8.0, ge=3.0, le=16.0)


class UserProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = None
    preferred_units: Optional[str] = None
    time_zone: Optional[str] = None
    fitness_goal: Optional[str] = None
    target_weight: Optional[float] = None
    daily_step_target: Optional[int] = None
    daily_water_target: Optional[int] = None
    daily_sleep_target: Optional[float] = None


class UserProfileOut(UserProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserProfileWithDetails(UserOut):
    profile: Optional[UserProfileOut] = None

    model_config = ConfigDict(from_attributes=True)
