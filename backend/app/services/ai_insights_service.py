from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.user import User, UserProfile
from backend.app.services.analytics_service import AnalyticsService


class AIInsightsService:
    @staticmethod
    def generate_weekly_insights(db: Session, user: User, target_date: date) -> Dict[str, Any]:
        """
        Analyzes the user's actual stored fitness data over the past week and
        synthesizes practical, habit-focused insights.
        """
        weekly_data = AnalyticsService.get_weekly_analytics(db, user, target_date)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        target_steps = profile.daily_step_target if profile else 10000
        target_sleep_hours = profile.daily_sleep_target if profile else 8.0
        target_water_ml = profile.daily_water_target if profile else 2500

        insights: List[Dict[str, str]] = []

        # 1. Workout Consistency Insight
        if weekly_data.total_workouts >= 4:
            insights.append({
                "category": "Workout Consistency",
                "badge": "High Momentum",
                "insight": f"Outstanding dedication! You recorded {weekly_data.total_workouts} workouts totaling {weekly_data.total_workout_minutes} minutes this week. Consistency is the biggest driver of long-term progress.",
            })
        elif weekly_data.total_workouts >= 2:
            insights.append({
                "category": "Workout Consistency",
                "badge": "On Track",
                "insight": f"Solid effort with {weekly_data.total_workouts} workouts logged ({weekly_data.total_workout_minutes} minutes). Adding one more focused session or an active recovery walk will build even greater resilience.",
            })
        else:
            insights.append({
                "category": "Workout Consistency",
                "badge": "Opportunity",
                "insight": f"You logged {weekly_data.total_workouts} workout(s) this week. Even two 20-minute bodyweight or cardio sessions can dramatically boost metabolism and mood.",
            })

        # 2. Daily Step Activity Insight
        if weekly_data.avg_daily_steps >= target_steps:
            insights.append({
                "category": "Daily Steps",
                "badge": "Goal Achieved",
                "insight": f"You averaged {weekly_data.avg_daily_steps:,} steps/day, beating your daily target of {target_steps:,}. Your Non-Exercise Activity Thermogenesis (NEAT) is in an excellent range.",
            })
        else:
            diff = target_steps - weekly_data.avg_daily_steps
            insights.append({
                "category": "Daily Steps",
                "badge": "Pacing",
                "insight": f"You averaged {weekly_data.avg_daily_steps:,} steps/day (target: {target_steps:,}). An extra 10-minute walk after meals can easily close the {diff:,} step gap.",
            })

        # 3. Sleep & Recovery Insight
        if weekly_data.avg_sleep_hours >= target_sleep_hours:
            insights.append({
                "category": "Sleep & Recovery",
                "badge": "Well Rested",
                "insight": f"You averaged {weekly_data.avg_sleep_hours} hours of sleep nightly. Good sleep supports muscular recovery, insulin sensitivity, and sustained cognitive focus.",
            })
        else:
            insights.append({
                "category": "Sleep & Recovery",
                "badge": "Recovery Alert",
                "insight": f"Your average sleep was {weekly_data.avg_sleep_hours}h vs your {target_sleep_hours}h goal. Prioritizing consistent wind-down habits and reducing late-night screen time can enhance your training output.",
            })

        # 4. Hydration Insight
        avg_water = int(weekly_data.total_water_ml / 7)
        if avg_water >= target_water_ml:
            insights.append({
                "category": "Hydration",
                "badge": "Optimal",
                "insight": f"Averaging {avg_water} ml/day meets your hydration target ({target_water_ml} ml). Optimal hydration directly supports joint lubrication and exercise stamina.",
            })
        else:
            insights.append({
                "category": "Hydration",
                "badge": "Hydration Gap",
                "insight": f"You averaged {avg_water} ml/day (goal: {target_water_ml} ml). Keeping a reusable water bottle near your desk or workout space helps build regular sipping habits.",
            })

        return {
            "week_start": weekly_data.start_date.isoformat(),
            "week_end": weekly_data.end_date.isoformat(),
            "analyzed_user": user.name,
            "insights_count": len(insights),
            "insights": insights,
            "disclaimer": "Fitness insights are algorithmic summaries of recorded data to support personal habit formation and do not constitute medical advice.",
        }
