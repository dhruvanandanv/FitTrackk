from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.weight import WeightEntry
from backend.app.schemas.weight import WeightCreate, WeightUpdate, WeightOut

router = APIRouter(prefix="/weight", tags=["Weight Tracking"])


@router.post("", response_model=WeightOut, status_code=status.HTTP_201_CREATED)
def create_weight_entry(
    data: WeightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for existing entry on the same date to avoid accidental duplicate constraint failures
    existing = (
        db.query(WeightEntry)
        .filter(WeightEntry.user_id == current_user.id, WeightEntry.measurement_date == data.measurement_date)
        .first()
    )
    if existing:
        existing.weight_kg = data.weight_kg
        if data.note is not None:
            existing.note = data.note
        db.commit()
        db.refresh(existing)
        return existing

    new_entry = WeightEntry(
        user_id=current_user.id,
        weight_kg=data.weight_kg,
        measurement_date=data.measurement_date,
        note=data.note,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@router.get("", response_model=List[WeightOut])
def get_weight_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WeightEntry).filter(WeightEntry.user_id == current_user.id)
    if start_date:
        query = query.filter(WeightEntry.measurement_date >= start_date)
    if end_date:
        query = query.filter(WeightEntry.measurement_date <= end_date)

    return query.order_by(WeightEntry.measurement_date.desc()).limit(limit).all()


@router.get("/{entry_id}", response_model=WeightOut)
def get_weight_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight record not found")
    return entry


@router.patch("/{entry_id}", response_model=WeightOut)
def update_weight_entry(
    entry_id: int,
    update_data: WeightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight record not found")

    data_dict = update_data.model_dump(exclude_unset=True)
    for key, val in data_dict.items():
        setattr(entry, key, val)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(WeightEntry).filter(
        WeightEntry.id == entry_id,
        WeightEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight record not found")

    db.delete(entry)
    db.commit()
    return None
