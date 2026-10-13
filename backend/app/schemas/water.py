from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class WaterCreate(BaseModel):
    quantity_ml: int = Field(..., gt=0, le=5000, description="Amount of water drunk in milliliters")
    timestamp: Optional[datetime] = None


class WaterOut(BaseModel):
    id: int
    user_id: int
    quantity_ml: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class WaterDaySummary(BaseModel):
    date: date
    total_ml: int
    target_ml: int
    percentage: float
    entries: List[WaterOut]
