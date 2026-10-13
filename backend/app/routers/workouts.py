from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.workout import Workout, WorkoutExercise
from backend.app.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutOut, WorkoutExerciseCreate

router = APIRouter(prefix="/workouts", tags=["Workouts & Training"])


@router.post("", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
def create_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = Workout(
        user_id=current_user.id,
        workout_name=data.workout_name,
        workout_type=data.workout_type,
        start_time=data.start_time,
        duration_minutes=data.duration_minutes,
        notes=data.notes,
        estimated_calories=data.estimated_calories,
    )
    db.add(workout)
    db.flush()

    for ex in data.exercises:
        exercise_obj = WorkoutExercise(
            workout_id=workout.id,
            exercise_name=ex.exercise_name,
            sets=ex.sets,
            repetitions=ex.repetitions,
            weight_used=ex.weight_used,
            duration_minutes=ex.duration_minutes,
            distance_km=ex.distance_km,
            notes=ex.notes,
        )
        db.add(exercise_obj)

    db.commit()
    db.refresh(workout)
    return workout


@router.get("", response_model=List[WorkoutOut])
def list_workouts(
    workout_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Workout).filter(Workout.user_id == current_user.id)
    if workout_type:
        query = query.filter(Workout.workout_type.ilike(f"%{workout_type}%"))
    if start_date:
        query = query.filter(Workout.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Workout.start_time <= datetime.combine(end_date, datetime.max.time()))

    return query.order_by(Workout.start_time.desc()).limit(limit).all()


@router.get("/{workout_id}", response_model=WorkoutOut)
def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return workout


@router.patch("/{workout_id}", response_model=WorkoutOut)
def update_workout(
    workout_id: int,
    data: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    update_dict = data.model_dump(exclude_unset=True)
    exercises_data = update_dict.pop("exercises", None)

    for k, v in update_dict.items():
        setattr(workout, k, v)

    if exercises_data is not None:
        # Replace exercises
        db.query(WorkoutExercise).filter(WorkoutExercise.workout_id == workout.id).delete()
        for ex in exercises_data:
            exercise_obj = WorkoutExercise(
                workout_id=workout.id,
                exercise_name=ex["exercise_name"],
                sets=ex.get("sets", 1),
                repetitions=ex.get("repetitions", 0),
                weight_used=ex.get("weight_used", 0.0),
                duration_minutes=ex.get("duration_minutes"),
                distance_km=ex.get("distance_km"),
                notes=ex.get("notes"),
            )
            db.add(exercise_obj)

    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    db.delete(workout)
    db.commit()
    return None
