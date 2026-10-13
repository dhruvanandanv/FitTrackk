from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.sleep import SleepEntry
from backend.app.schemas.sleep import SleepCreate, SleepUpdate, SleepOut
from backend.app.utils.date_utils import calculate_sleep_duration

router = APIRouter(prefix="/sleep", tags=["Sleep Tracking"])


@router.post("", response_model=SleepOut, status_code=status.HTTP_201_CREATED)
def record_sleep(
    data: SleepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    duration = calculate_sleep_duration(data.sleep_start, data.sleep_end)
    entry = SleepEntry(
        user_id=current_user.id,
        sleep_start=data.sleep_start,
        sleep_end=data.sleep_end,
        duration_minutes=duration,
        quality_rating=data.quality_rating,
        data_source=data.data_source,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[SleepOut])
def get_sleep_history(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == current_user.id)
        .order_by(SleepEntry.sleep_start.desc())
        .limit(limit)
        .all()
    )


@router.patch("/{entry_id}", response_model=SleepOut)
def update_sleep_entry(
    entry_id: int,
    data: SleepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(SleepEntry).filter(
        SleepEntry.id == entry_id,
        SleepEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep record not found")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(entry, k, v)

    # Re-calculate duration
    entry.duration_minutes = calculate_sleep_duration(entry.sleep_start, entry.sleep_end)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(SleepEntry).filter(
        SleepEntry.id == entry_id,
        SleepEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep record not found")

    db.delete(entry)
    db.commit()
    return None
