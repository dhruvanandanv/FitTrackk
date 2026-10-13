from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class WeightCreate(BaseModel):
    weight_kg: float = Field(..., gt=15.0, lt=500.0, description="Weight in kilograms")
    measurement_date: date
    note: Optional[str] = Field(None, max_length=500)


class WeightUpdate(BaseModel):
    weight_kg: Optional[float] = Field(None, gt=15.0, lt=500.0)
    measurement_date: Optional[date] = None
    note: Optional[str] = Field(None, max_length=500)


class WeightOut(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    measurement_date: date
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
