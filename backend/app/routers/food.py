from datetime import datetime, date, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.food import FoodEntry
from backend.app.schemas.food import FoodCreate, FoodUpdate, FoodOut, FoodDaySummary
from backend.app.services.nutrition_service import NutritionService
from backend.app.utils.date_utils import parse_date

router = APIRouter(prefix="/food", tags=["Nutrition & Calories"])


@router.post("", response_model=FoodOut, status_code=status.HTTP_201_CREATED)
def log_food(
    data: FoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consumed_at = data.consumed_at or datetime.now(timezone.utc)
    entry = FoodEntry(
        user_id=current_user.id,
        food_name=data.food_name,
        meal_category=data.meal_category,
        serving_quantity=data.serving_quantity,
        calories=data.calories,
        protein_g=data.protein_g,
        carbs_g=data.carbs_g,
        fat_g=data.fat_g,
        consumed_at=consumed_at,
        data_source=data.data_source,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=FoodDaySummary)
def get_daily_food(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    entries = (
        db.query(FoodEntry)
        .filter(
            FoodEntry.user_id == current_user.id,
            FoodEntry.consumed_at >= start_of_day,
            FoodEntry.consumed_at <= end_of_day,
        )
        .order_by(FoodEntry.consumed_at.asc())
        .all()
    )

    total_cals = sum(e.calories for e in entries)
    total_protein = sum(e.protein_g for e in entries)
    total_carbs = sum(e.carbs_g for e in entries)
    total_fat = sum(e.fat_g for e in entries)

    return FoodDaySummary(
        date=target_date,
        total_calories=round(total_cals, 1),
        total_protein_g=round(total_protein, 1),
        total_carbs_g=round(total_carbs, 1),
        total_fat_g=round(total_fat, 1),
        entries=[FoodOut.model_validate(e) for e in entries],
    )


@router.get("/search")
async def search_nutrition(
    q: str = Query(..., min_length=1, description="Food name to search"),
    current_user: User = Depends(get_current_user),
):
    results = await NutritionService.search_food(q)
    return {"query": q, "results": results}


@router.patch("/{entry_id}", response_model=FoodOut)
def update_food_entry(
    entry_id: int,
    data: FoodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(FoodEntry).filter(
        FoodEntry.id == entry_id,
        FoodEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food entry not found")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(entry, k, v)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(FoodEntry).filter(
        FoodEntry.id == entry_id,
        FoodEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food entry not found")

    db.delete(entry)
    db.commit()
    return None
