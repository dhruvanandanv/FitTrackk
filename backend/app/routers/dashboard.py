from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.dashboard import TodaySummary
from backend.app.services.dashboard_service import DashboardService
from backend.app.utils.date_utils import parse_date

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=TodaySummary)
def get_dashboard(
    date_str: Optional[str] = Query(None, alias="date", description="Target date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    return DashboardService.get_dashboard_summary(db, current_user, target_date)
