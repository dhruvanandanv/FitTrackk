from datetime import date, datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.user import User, UserProfile
from backend.app.models.weight import WeightEntry
from backend.app.models.activity import DailyActivity
from backend.app.models.workout import Workout, WorkoutExercise
from backend.app.models.water import WaterEntry
from backend.app.models.sleep import SleepEntry
from backend.app.models.food import FoodEntry
from backend.app.schemas.analytics import (
    WeeklyAnalyticsResponse, MonthlyAnalyticsResponse,
    WeightAnalyticsResponse, WorkoutAnalyticsResponse, DayMetric
)
from backend.app.schemas.weight import WeightOut
from backend.app.utils.date_utils import get_week_range, get_month_range


class AnalyticsService:
    @staticmethod
    def get_weekly_analytics(db: Session, user: User, target_date: date) -> WeeklyAnalyticsResponse:
        start_date, end_date = get_week_range(target_date)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        step_target = profile.daily_step_target if profile else 10000

        days_metrics: List[DayMetric] = []
        total_steps = 0
        total_water = 0
        total_sleep_mins = 0
        total_cals_in = 0.0
        total_cals_out = 0.0
        total_workout_mins = 0
        total_workouts = 0
        days_met_step_goal = 0

        current = start_date
        while current <= end_date:
            c_start = datetime.combine(current, datetime.min.time())
            c_end = datetime.combine(current, datetime.max.time())

            # Activity
            act = db.query(DailyActivity).filter(
                DailyActivity.user_id == user.id, DailyActivity.activity_date == current
            ).first()
            steps = act.steps if act else 0
            act_mins = act.active_minutes if act else 0
            act_cals = act.calories_burned if (act and act.calories_burned) else 0.0

            if steps >= step_target:
                days_met_step_goal += 1

            # Water
            water_sum = db.query(func.coalesce(func.sum(WaterEntry.quantity_ml), 0)).filter(
                WaterEntry.user_id == user.id,
                WaterEntry.timestamp >= c_start,
                WaterEntry.timestamp <= c_end
            ).scalar()

            # Sleep
            sleeps = db.query(SleepEntry).filter(
                SleepEntry.user_id == user.id,
                func.date(SleepEntry.sleep_end) == current
            ).all()
            sleep_mins = sum(s.duration_minutes for s in sleeps)

            # Food
            food_cals = db.query(func.coalesce(func.sum(FoodEntry.calories), 0.0)).filter(
                FoodEntry.user_id == user.id,
                FoodEntry.consumed_at >= c_start,
                FoodEntry.consumed_at <= c_end
            ).scalar()

            # Workouts
            workouts = db.query(Workout).filter(
                Workout.user_id == user.id,
                Workout.start_time >= c_start,
                Workout.start_time <= c_end
            ).all()
            w_mins = sum(w.duration_minutes for w in workouts)
            w_cals = sum(w.estimated_calories or 0.0 for w in workouts)
            total_workouts += len(workouts)

            day_metric = DayMetric(
                date=current,
                steps=steps,
                active_minutes=act_mins,
                water_ml=water_sum,
                sleep_minutes=sleep_mins,
                calories_consumed=round(food_cals, 1),
                calories_burned=round(act_cals + w_cals, 1),
                workout_minutes=w_mins,
            )
            days_metrics.append(day_metric)

            total_steps += steps
            total_water += water_sum
            total_sleep_mins += sleep_mins
            total_cals_in += food_cals
            total_cals_out += (act_cals + w_cals)
            total_workout_mins += w_mins

            current += timedelta(days=1)

        days_count = len(days_metrics) or 1
        goal_completion_rate = round((days_met_step_goal / days_count) * 100, 1)

        return WeeklyAnalyticsResponse(
            start_date=start_date,
            end_date=end_date,
            total_steps=total_steps,
            avg_daily_steps=int(total_steps / days_count),
            total_workouts=total_workouts,
            total_workout_minutes=total_workout_mins,
            total_water_ml=total_water,
            avg_sleep_hours=round((total_sleep_mins / days_count) / 60.0, 1),
            total_calories_consumed=round(total_cals_in, 1),
            total_calories_burned=round(total_cals_out, 1),
            goal_completion_rate=goal_completion_rate,
            days=days_metrics,
        )

    @staticmethod
    def get_monthly_analytics(db: Session, user: User, target_date: date) -> MonthlyAnalyticsResponse:
        start_date, end_date = get_month_range(target_date)
        days_metrics: List[DayMetric] = []
        total_steps = 0
        total_workout_mins = 0
        total_cals_in = 0.0
        total_workouts = 0

        current = start_date
        while current <= end_date:
            c_start = datetime.combine(current, datetime.min.time())
            c_end = datetime.combine(current, datetime.max.time())

            act = db.query(DailyActivity).filter(
                DailyActivity.user_id == user.id, DailyActivity.activity_date == current
            ).first()
            steps = act.steps if act else 0
            act_mins = act.active_minutes if act else 0
            act_cals = act.calories_burned if (act and act.calories_burned) else 0.0

            water_sum = db.query(func.coalesce(func.sum(WaterEntry.quantity_ml), 0)).filter(
                WaterEntry.user_id == user.id,
                WaterEntry.timestamp >= c_start,
                WaterEntry.timestamp <= c_end
            ).scalar()

            sleeps = db.query(SleepEntry).filter(
                SleepEntry.user_id == user.id,
                func.date(SleepEntry.sleep_end) == current
            ).all()
            sleep_mins = sum(s.duration_minutes for s in sleeps)

            food_cals = db.query(func.coalesce(func.sum(FoodEntry.calories), 0.0)).filter(
                FoodEntry.user_id == user.id,
                FoodEntry.consumed_at >= c_start,
                FoodEntry.consumed_at <= c_end
            ).scalar()

            workouts = db.query(Workout).filter(
                Workout.user_id == user.id,
                Workout.start_time >= c_start,
                Workout.start_time <= c_end
            ).all()
            w_mins = sum(w.duration_minutes for w in workouts)
            w_cals = sum(w.estimated_calories or 0.0 for w in workouts)
            total_workouts += len(workouts)

            day_metric = DayMetric(
                date=current,
                steps=steps,
                active_minutes=act_mins,
                water_ml=water_sum,
                sleep_minutes=sleep_mins,
                calories_consumed=round(food_cals, 1),
                calories_burned=round(act_cals + w_cals, 1),
                workout_minutes=w_mins,
            )
            days_metrics.append(day_metric)

            total_steps += steps
            total_cals_in += food_cals
            total_workout_mins += w_mins

            current += timedelta(days=1)

        days_count = len(days_metrics) or 1
        return MonthlyAnalyticsResponse(
            start_date=start_date,
            end_date=end_date,
            total_steps=total_steps,
            avg_daily_steps=int(total_steps / days_count),
            total_workouts=total_workouts,
            total_workout_minutes=total_workout_mins,
            total_calories_consumed=round(total_cals_in, 1),
            days=days_metrics,
        )

    @staticmethod
    def get_weight_analytics(db: Session, user: User) -> WeightAnalyticsResponse:
        history_db = (
            db.query(WeightEntry)
            .filter(WeightEntry.user_id == user.id)
            .order_by(WeightEntry.measurement_date.asc())
            .all()
        )
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        target_weight = profile.target_weight if profile else None
        goal_type = profile.fitness_goal if profile else "maintain"

        history = [WeightOut.model_validate(w) for w in history_db]
        if not history:
            return WeightAnalyticsResponse(
                latest_weight=None,
                earliest_weight=None,
                weight_change=None,
                target_weight=target_weight,
                progress_percentage=None,
                goal_type=goal_type,
                history=[],
            )

        earliest = history[0].weight_kg
        latest = history[-1].weight_kg
        change = round(latest - earliest, 1)

        progress_pct = None
        if target_weight and earliest != target_weight:
            # calculate progress towards target
            total_distance = abs(target_weight - earliest)
            current_distance = abs(target_weight - latest)
            if total_distance > 0:
                raw_progress = ((total_distance - current_distance) / total_distance) * 100.0
                progress_pct = round(max(0.0, min(100.0, raw_progress)), 1)

        return WeightAnalyticsResponse(
            latest_weight=latest,
            earliest_weight=earliest,
            weight_change=change,
            target_weight=target_weight,
            progress_percentage=progress_pct,
            goal_type=goal_type,
            history=history,
        )

    @staticmethod
    def get_workout_analytics(db: Session, user: User) -> WorkoutAnalyticsResponse:
        workouts = db.query(Workout).filter(Workout.user_id == user.id).all()
        total_workouts = len(workouts)
        total_duration = sum(w.duration_minutes for w in workouts)

        by_type: Dict[str, int] = {}
        for w in workouts:
            wtype = w.workout_type or "other"
            by_type[wtype] = by_type.get(wtype, 0) + 1

        recent_exercises = (
            db.query(WorkoutExercise.exercise_name)
            .join(Workout, Workout.id == WorkoutExercise.workout_id)
            .filter(Workout.user_id == user.id)
            .order_by(Workout.start_time.desc())
            .distinct()
            .limit(10)
            .all()
        )
        exercise_names = [e[0] for e in recent_exercises]

        return WorkoutAnalyticsResponse(
            total_workouts=total_workouts,
            total_duration_minutes=total_duration,
            by_type=by_type,
            recent_exercises=exercise_names,
        )
