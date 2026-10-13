from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FoodCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=200)
    meal_category: str = Field("snack", pattern="^(breakfast|lunch|dinner|snack)$")
    serving_quantity: float = Field(1.0, gt=0, le=100.0)
    calories: float = Field(..., ge=0.0, le=10000.0)
    protein_g: float = Field(0.0, ge=0.0, le=1000.0)
    carbs_g: float = Field(0.0, ge=0.0, le=1000.0)
    fat_g: float = Field(0.0, ge=0.0, le=1000.0)
    consumed_at: Optional[datetime] = None
    data_source: str = "manual"


class FoodUpdate(BaseModel):
    food_name: Optional[str] = Field(None, min_length=1, max_length=200)
    meal_category: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    serving_quantity: Optional[float] = Field(None, gt=0, le=100.0)
    calories: Optional[float] = Field(None, ge=0.0, le=10000.0)
    protein_g: Optional[float] = Field(None, ge=0.0, le=1000.0)
    carbs_g: Optional[float] = Field(None, ge=0.0, le=1000.0)
    fat_g: Optional[float] = Field(None, ge=0.0, le=1000.0)
    consumed_at: Optional[datetime] = None
    data_source: Optional[str] = None


class FoodOut(BaseModel):
    id: int
    user_id: int
    food_name: str
    meal_category: str
    serving_quantity: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    consumed_at: datetime
    data_source: str

    model_config = ConfigDict(from_attributes=True)


class FoodDaySummary(BaseModel):
    date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    entries: List[FoodOut]
