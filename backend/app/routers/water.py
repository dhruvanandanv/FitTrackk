from datetime import datetime, date, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User, UserProfile
from backend.app.models.water import WaterEntry
from backend.app.schemas.water import WaterCreate, WaterOut, WaterDaySummary
from backend.app.utils.date_utils import parse_date

router = APIRouter(prefix="/water", tags=["Water & Hydration"])


@router.post("", response_model=WaterOut, status_code=status.HTTP_201_CREATED)
def log_water(
    data: WaterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry_time = data.timestamp or datetime.now(timezone.utc)
    entry = WaterEntry(
        user_id=current_user.id,
        quantity_ml=data.quantity_ml,
        timestamp=entry_time,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=WaterDaySummary)
def get_daily_water(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    entries = (
        db.query(WaterEntry)
        .filter(
            WaterEntry.user_id == current_user.id,
            WaterEntry.timestamp >= start_of_day,
            WaterEntry.timestamp <= end_of_day,
        )
        .order_by(WaterEntry.timestamp.desc())
        .all()
    )

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    target_ml = profile.daily_water_target if profile else 2500
    total_ml = sum(e.quantity_ml for e in entries)
    percentage = round((total_ml / target_ml * 100), 1) if target_ml > 0 else 0.0

    return WaterDaySummary(
        date=target_date,
        total_ml=total_ml,
        target_ml=target_ml,
        percentage=percentage,
        entries=[WaterOut.model_validate(e) for e in entries],
    )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(WaterEntry).filter(
        WaterEntry.id == entry_id,
        WaterEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Water entry not found")

    db.delete(entry)
    db.commit()
    return None
