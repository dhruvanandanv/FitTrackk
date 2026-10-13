from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.analytics import (
    WeeklyAnalyticsResponse, MonthlyAnalyticsResponse,
    WeightAnalyticsResponse, WorkoutAnalyticsResponse
)
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.export_service import ExportService
from backend.app.utils.date_utils import parse_date

router = APIRouter(prefix="/analytics", tags=["Analytics & Reports"])


@router.get("/weekly", response_model=WeeklyAnalyticsResponse)
def get_weekly_analytics(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    return AnalyticsService.get_weekly_analytics(db, current_user, target_date)


@router.get("/monthly", response_model=MonthlyAnalyticsResponse)
def get_monthly_analytics(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    return AnalyticsService.get_monthly_analytics(db, current_user, target_date)


@router.get("/weight", response_model=WeightAnalyticsResponse)
def get_weight_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_weight_analytics(db, current_user)


@router.get("/workouts", response_model=WorkoutAnalyticsResponse)
def get_workout_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_workout_analytics(db, current_user)


@router.get("/export")
def export_fitness_data(
    data_type: str = Query("all", pattern="^(all|weight|activity|workouts|food|water|sleep)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    csv_data = ExportService.export_csv(db, current_user, data_type=data_type)
    filename = f"fittrack_{current_user.name.lower().replace(' ', '_')}_{data_type}_{date.today().isoformat()}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
