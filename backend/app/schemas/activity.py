from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ActivityCreate(BaseModel):
    activity_date: date
    steps: int = Field(0, ge=0, le=200000)
    active_minutes: int = Field(0, ge=0, le=1440)
    cardio_minutes: int = Field(0, ge=0, le=1440)
    calories_burned: Optional[float] = Field(None, ge=0.0, le=10000.0)
    data_source: str = "manual"


class ActivityUpdate(BaseModel):
    steps: Optional[int] = Field(None, ge=0, le=200000)
    active_minutes: Optional[int] = Field(None, ge=0, le=1440)
    cardio_minutes: Optional[int] = Field(None, ge=0, le=1440)
    calories_burned: Optional[float] = Field(None, ge=0.0, le=10000.0)
    data_source: Optional[str] = None


class ActivityOut(BaseModel):
    id: int
    user_id: int
    activity_date: date
    steps: int
    active_minutes: int
    cardio_minutes: int
    calories_burned: Optional[float] = None
    data_source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
