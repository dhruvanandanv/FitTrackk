from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.activity import DailyActivity
from backend.app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityOut

router = APIRouter(prefix="/activity", tags=["Daily Activity & Steps"])


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def record_daily_activity(
    data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Upsert pattern for daily activity summary per user and date
    existing = (
        db.query(DailyActivity)
        .filter(DailyActivity.user_id == current_user.id, DailyActivity.activity_date == data.activity_date)
        .first()
    )
    if existing:
        existing.steps = data.steps
        existing.active_minutes = data.active_minutes
        existing.cardio_minutes = data.cardio_minutes
        if data.calories_burned is not None:
            existing.calories_burned = data.calories_burned
        existing.data_source = data.data_source
        db.commit()
        db.refresh(existing)
        return existing

    new_act = DailyActivity(
        user_id=current_user.id,
        activity_date=data.activity_date,
        steps=data.steps,
        active_minutes=data.active_minutes,
        cardio_minutes=data.cardio_minutes,
        calories_burned=data.calories_burned,
        data_source=data.data_source,
    )
    db.add(new_act)
    db.commit()
    db.refresh(new_act)
    return new_act


@router.get("", response_model=List[ActivityOut])
def get_activities(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(DailyActivity).filter(DailyActivity.user_id == current_user.id)
    if start_date:
        query = query.filter(DailyActivity.activity_date >= start_date)
    if end_date:
        query = query.filter(DailyActivity.activity_date <= end_date)

    return query.order_by(DailyActivity.activity_date.desc()).limit(limit).all()


@router.patch("/{entry_id}", response_model=ActivityOut)
def update_activity(
    entry_id: int,
    data: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(DailyActivity).filter(
        DailyActivity.id == entry_id,
        DailyActivity.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity record not found")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(entry, k, v)

    db.commit()
    db.refresh(entry)
    return entry
