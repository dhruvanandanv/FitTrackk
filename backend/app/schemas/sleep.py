from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SleepCreate(BaseModel):
    sleep_start: datetime
    sleep_end: datetime
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    data_source: str = "manual"


class SleepUpdate(BaseModel):
    sleep_start: Optional[datetime] = None
    sleep_end: Optional[datetime] = None
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    data_source: Optional[str] = None


class SleepOut(BaseModel):
    id: int
    user_id: int
    sleep_start: datetime
    sleep_end: datetime
    duration_minutes: int
    quality_rating: Optional[int] = None
    data_source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
