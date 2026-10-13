from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.user import User, UserProfile
from backend.app.models.weight import WeightEntry
from backend.app.models.activity import DailyActivity
from backend.app.models.workout import Workout
from backend.app.models.water import WaterEntry
from backend.app.models.sleep import SleepEntry
from backend.app.models.food import FoodEntry
from backend.app.schemas.dashboard import TodaySummary, MetricProgress
from backend.app.schemas.workout import WorkoutOut


class DashboardService:
    @staticmethod
    def get_dashboard_summary(db: Session, user: User, target_date: date) -> TodaySummary:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        step_target = profile.daily_step_target if profile else 10000
        water_target = profile.daily_water_target if profile else 2500
        sleep_target_hours = profile.daily_sleep_target if profile else 8.0
        sleep_target_minutes = int(sleep_target_hours * 60)
        target_weight = profile.target_weight if profile else None

        # Greeting based on current hour
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # 1. Weight: Latest weight entry up to target_date
        latest_weight_entry = (
            db.query(WeightEntry)
            .filter(WeightEntry.user_id == user.id, WeightEntry.measurement_date <= target_date)
            .order_by(WeightEntry.measurement_date.desc(), WeightEntry.created_at.desc())
            .first()
        )
        current_weight = latest_weight_entry.weight_kg if latest_weight_entry else None

        # Earliest weight entry for overall change
        earliest_weight_entry = (
            db.query(WeightEntry)
            .filter(WeightEntry.user_id == user.id)
            .order_by(WeightEntry.measurement_date.asc(), WeightEntry.created_at.asc())
            .first()
        )
        weight_change = None
        if latest_weight_entry and earliest_weight_entry:
            weight_change = round(latest_weight_entry.weight_kg - earliest_weight_entry.weight_kg, 1)

        # BMI screening calculation if height is available
        bmi = None
        if current_weight and profile and profile.height_cm and profile.height_cm > 0:
            height_m = profile.height_cm / 100.0
            bmi = round(current_weight / (height_m * height_m), 1)

        # 2. Steps & Daily Activity for target_date
        activity_today = (
            db.query(DailyActivity)
            .filter(DailyActivity.user_id == user.id, DailyActivity.activity_date == target_date)
            .first()
        )
        today_steps = activity_today.steps if activity_today else 0
        step_pct_actual = round((today_steps / step_target * 100), 1) if step_target > 0 else 0.0
        step_progress = MetricProgress(
            current=float(today_steps),
            target=float(step_target),
            percentage=min(100.0, step_pct_actual),
            actual_percentage=step_pct_actual,
            unit="steps",
        )

        # 3. Water Intake for target_date
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        water_today_sum = (
            db.query(func.coalesce(func.sum(WaterEntry.quantity_ml), 0))
            .filter(
                WaterEntry.user_id == user.id,
                WaterEntry.timestamp >= start_of_day,
                WaterEntry.timestamp <= end_of_day,
            )
            .scalar()
        )
        water_pct_actual = round((water_today_sum / water_target * 100), 1) if water_target > 0 else 0.0
        water_progress = MetricProgress(
            current=float(water_today_sum),
            target=float(water_target),
            percentage=min(100.0, water_pct_actual),
            actual_percentage=water_pct_actual,
            unit="ml",
        )

        # 4. Sleep for target_date (sleep session that ended or started on target_date)
        sleep_today_entries = (
            db.query(SleepEntry)
            .filter(
                SleepEntry.user_id == user.id,
                func.date(SleepEntry.sleep_end) == target_date,
            )
            .all()
        )
        total_sleep_minutes = sum(s.duration_minutes for s in sleep_today_entries)
        sleep_pct_actual = (
            round((total_sleep_minutes / sleep_target_minutes * 100), 1)
            if sleep_target_minutes > 0
            else 0.0
        )
        sleep_progress = MetricProgress(
            current=round(total_sleep_minutes / 60.0, 1),
            target=float(sleep_target_hours),
            percentage=min(100.0, sleep_pct_actual),
            actual_percentage=sleep_pct_actual,
            unit="hours",
        )

        # 5. Nutrition / Food Intake for target_date
        food_calories = (
            db.query(func.coalesce(func.sum(FoodEntry.calories), 0.0))
            .filter(
                FoodEntry.user_id == user.id,
                FoodEntry.consumed_at >= start_of_day,
                FoodEntry.consumed_at <= end_of_day,
            )
            .scalar()
        )

        # 6. Workouts for target_date
        workouts_today = (
            db.query(Workout)
            .filter(
                Workout.user_id == user.id,
                Workout.start_time >= start_of_day,
                Workout.start_time <= end_of_day,
            )
            .all()
        )
        workouts_count = len(workouts_today)
        workouts_duration_minutes = sum(w.duration_minutes for w in workouts_today)
        workout_calories_burned = sum(w.estimated_calories or 0.0 for w in workouts_today)
        activity_calories_burned = activity_today.calories_burned if (activity_today and activity_today.calories_burned) else 0.0
        total_calories_burned = round(workout_calories_burned + activity_calories_burned, 1)

        # 7. Recent workouts (latest 5)
        recent_workouts_db = (
            db.query(Workout)
            .filter(Workout.user_id == user.id)
            .order_by(Workout.start_time.desc())
            .limit(5)
            .all()
        )
        recent_workouts = [WorkoutOut.model_validate(w) for w in recent_workouts_db]

        # 8. Weekly activity trend (last 7 days up to target_date)
        weekly_activity_trend: List[Dict[str, Any]] = []
        for i in range(6, -1, -1):
            day_date = target_date - timedelta(days=i)
            day_activity = (
                db.query(DailyActivity)
                .filter(DailyActivity.user_id == user.id, DailyActivity.activity_date == day_date)
                .first()
            )
            day_start = datetime.combine(day_date, datetime.min.time())
            day_end = datetime.combine(day_date, datetime.max.time())
            day_workout_mins = (
                db.query(func.coalesce(func.sum(Workout.duration_minutes), 0))
                .filter(
                    Workout.user_id == user.id,
                    Workout.start_time >= day_start,
                    Workout.start_time <= day_end,
                )
                .scalar()
            )
            weekly_activity_trend.append({
                "date": day_date.isoformat(),
                "day_name": day_date.strftime("%a"),
                "steps": day_activity.steps if day_activity else 0,
                "active_minutes": day_activity.active_minutes if day_activity else 0,
                "workout_minutes": day_workout_mins,
            })

        # 9. Weight trend (last 10 entries)
        weight_trend_db = (
            db.query(WeightEntry)
            .filter(WeightEntry.user_id == user.id)
            .order_by(WeightEntry.measurement_date.asc())
            .limit(10)
            .all()
        )
        weight_trend = [
            {"date": w.measurement_date.isoformat(), "weight": w.weight_kg}
            for w in weight_trend_db
        ]

        return TodaySummary(
            date=target_date,
            greeting=greeting,
            user_name=user.name,
            current_weight=current_weight,
            target_weight=target_weight,
            weight_change=weight_change,
            bmi=bmi,
            steps=step_progress,
            water=water_progress,
            sleep=sleep_progress,
            calories_consumed=round(food_calories, 1),
            calories_burned=total_calories_burned,
            workouts_count=workouts_count,
            workouts_duration_minutes=workouts_duration_minutes,
            recent_workouts=recent_workouts,
            weekly_activity_trend=weekly_activity_trend,
            weight_trend=weight_trend,
        )
