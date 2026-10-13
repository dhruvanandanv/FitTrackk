import csv
import io
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.weight import WeightEntry
from backend.app.models.activity import DailyActivity
from backend.app.models.workout import Workout, WorkoutExercise
from backend.app.models.water import WaterEntry
from backend.app.models.sleep import SleepEntry
from backend.app.models.food import FoodEntry


class ExportService:
    @staticmethod
    def export_csv(db: Session, user: User, data_type: str = "all") -> str:
        """
        Exports user fitness records to CSV format.
        Guarantees only data belonging to `user.id` is included.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        if data_type in ("all", "weight"):
            writer.writerow(["--- WEIGHT RECORDS ---"])
            writer.writerow(["Date", "Weight (kg)", "Note", "Logged At"])
            weights = (
                db.query(WeightEntry)
                .filter(WeightEntry.user_id == user.id)
                .order_by(WeightEntry.measurement_date.asc())
                .all()
            )
            for w in weights:
                writer.writerow([w.measurement_date, w.weight_kg, w.note or "", w.created_at.isoformat()])
            writer.writerow([])

        if data_type in ("all", "activity"):
            writer.writerow(["--- DAILY ACTIVITY RECORDS ---"])
            writer.writerow(["Date", "Steps", "Active Minutes", "Cardio Minutes", "Calories Burned", "Source"])
            activities = (
                db.query(DailyActivity)
                .filter(DailyActivity.user_id == user.id)
                .order_by(DailyActivity.activity_date.asc())
                .all()
            )
            for a in activities:
                writer.writerow([a.activity_date, a.steps, a.active_minutes, a.cardio_minutes, a.calories_burned or 0.0, a.data_source])
            writer.writerow([])

        if data_type in ("all", "workouts"):
            writer.writerow(["--- WORKOUT RECORDS ---"])
            writer.writerow(["Date & Time", "Workout Name", "Type", "Duration (mins)", "Calories", "Exercise Name", "Sets", "Reps", "Weight (kg)"])
            workouts = (
                db.query(Workout)
                .filter(Workout.user_id == user.id)
                .order_by(Workout.start_time.asc())
                .all()
            )
            for w in workouts:
                if w.exercises:
                    for ex in w.exercises:
                        writer.writerow([w.start_time.isoformat(), w.workout_name, w.workout_type, w.duration_minutes, w.estimated_calories or 0.0, ex.exercise_name, ex.sets, ex.repetitions, ex.weight_used])
                else:
                    writer.writerow([w.start_time.isoformat(), w.workout_name, w.workout_type, w.duration_minutes, w.estimated_calories or 0.0, "None", 0, 0, 0.0])
            writer.writerow([])

        if data_type in ("all", "food"):
            writer.writerow(["--- NUTRITION & FOOD RECORDS ---"])
            writer.writerow(["Consumed At", "Food Name", "Category", "Serving Qty", "Calories", "Protein (g)", "Carbs (g)", "Fat (g)", "Source"])
            foods = (
                db.query(FoodEntry)
                .filter(FoodEntry.user_id == user.id)
                .order_by(FoodEntry.consumed_at.asc())
                .all()
            )
            for f in foods:
                writer.writerow([f.consumed_at.isoformat(), f.food_name, f.meal_category, f.serving_quantity, f.calories, f.protein_g, f.carbs_g, f.fat_g, f.data_source])
            writer.writerow([])

        if data_type in ("all", "water"):
            writer.writerow(["--- WATER RECORDS ---"])
            writer.writerow(["Timestamp", "Quantity (ml)"])
            waters = (
                db.query(WaterEntry)
                .filter(WaterEntry.user_id == user.id)
                .order_by(WaterEntry.timestamp.asc())
                .all()
            )
            for wt in waters:
                writer.writerow([wt.timestamp.isoformat(), wt.quantity_ml])
            writer.writerow([])

        if data_type in ("all", "sleep"):
            writer.writerow(["--- SLEEP RECORDS ---"])
            writer.writerow(["Start Time", "End Time", "Duration (mins)", "Duration (hours)", "Quality Rating (1-5)", "Source"])
            sleeps = (
                db.query(SleepEntry)
                .filter(SleepEntry.user_id == user.id)
                .order_by(SleepEntry.sleep_start.asc())
                .all()
            )
            for s in sleeps:
                writer.writerow([s.sleep_start.isoformat(), s.sleep_end.isoformat(), s.duration_minutes, round(s.duration_minutes / 60.0, 1), s.quality_rating or "", s.data_source])
            writer.writerow([])

        return output.getvalue()
