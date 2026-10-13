from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.services.exercise_service import ExerciseService
from backend.app.services.weather_service import WeatherService
from backend.app.services.ai_insights_service import AIInsightsService
from backend.app.utils.date_utils import parse_date

router = APIRouter(tags=["Integrations & AI Insights"])


@router.get("/integrations/nutrition/status")
def get_nutrition_status():
    return {
        "provider": "USDA FoodData Central / Curated Reference DB",
        "api_key_configured": bool(settings.USDA_API_KEY),
        "status": "ready",
        "features": ["Calorie search", "Macronutrient breakdown", "Offline fallback"]
    }


@router.get("/integrations/exercises/status")
def get_exercises_status():
    return {
        "provider": "FitTrack Exercise Knowledge Base",
        "status": "ready",
        "total_exercises_cataloged": len(ExerciseService.search_exercises()),
        "categories": ["strength", "calisthenics", "cardio", "core"]
    }


@router.get("/integrations/exercises")
def search_exercises(
    q: Optional[str] = Query(None, description="Search query"),
    muscle_group: Optional[str] = Query(None, description="Target muscle group"),
    current_user: User = Depends(get_current_user),
):
    return ExerciseService.search_exercises(query=q, muscle_group=muscle_group)


@router.get("/integrations/weather")
async def get_workout_weather(
    lat: float = Query(40.7128, description="Latitude"),
    lon: float = Query(-74.0060, description="Longitude"),
    current_user: User = Depends(get_current_user),
):
    return await WeatherService.get_workout_weather(latitude=lat, longitude=lon)


@router.post("/insights/weekly")
def get_weekly_insights(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = parse_date(date_str) if date_str else date.today()
    return AIInsightsService.generate_weekly_insights(db, current_user, target_date)
