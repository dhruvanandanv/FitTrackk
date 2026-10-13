"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-12 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # User Profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('preferred_units', sa.String(length=20), nullable=False),
        sa.Column('time_zone', sa.String(length=50), nullable=False),
        sa.Column('fitness_goal', sa.String(length=50), nullable=False),
        sa.Column('target_weight', sa.Float(), nullable=True),
        sa.Column('daily_step_target', sa.Integer(), nullable=False),
        sa.Column('daily_water_target', sa.Integer(), nullable=False),
        sa.Column('daily_sleep_target', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)

    # Weight Entries table
    op.create_table(
        'weight_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('measurement_date', sa.Date(), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'measurement_date', name='uq_user_weight_date')
    )
    op.create_index(op.f('ix_weight_entries_id'), 'weight_entries', ['id'], unique=False)
    op.create_index(op.f('ix_weight_entries_measurement_date'), 'weight_entries', ['measurement_date'], unique=False)
    op.create_index(op.f('ix_weight_entries_user_id'), 'weight_entries', ['user_id'], unique=False)

    # Daily Activities table
    op.create_table(
        'daily_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_date', sa.Date(), nullable=False),
        sa.Column('steps', sa.Integer(), nullable=False),
        sa.Column('active_minutes', sa.Integer(), nullable=False),
        sa.Column('cardio_minutes', sa.Integer(), nullable=False),
        sa.Column('calories_burned', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'activity_date', name='uq_user_activity_date')
    )
    op.create_index(op.f('ix_daily_activities_activity_date'), 'daily_activities', ['activity_date'], unique=False)
    op.create_index(op.f('ix_daily_activities_id'), 'daily_activities', ['id'], unique=False)
    op.create_index(op.f('ix_daily_activities_user_id'), 'daily_activities', ['user_id'], unique=False)

    # Workouts table
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workout_name', sa.String(length=150), nullable=False),
        sa.Column('workout_type', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('estimated_calories', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workouts_id'), 'workouts', ['id'], unique=False)
    op.create_index(op.f('ix_workouts_start_time'), 'workouts', ['start_time'], unique=False)
    op.create_index(op.f('ix_workouts_user_id'), 'workouts', ['user_id'], unique=False)
    op.create_index(op.f('ix_workouts_workout_type'), 'workouts', ['workout_type'], unique=False)

    # Workout Exercises table
    op.create_table(
        'workout_exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('exercise_name', sa.String(length=150), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('repetitions', sa.Integer(), nullable=False),
        sa.Column('weight_used', sa.Float(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_exercises_id'), 'workout_exercises', ['id'], unique=False)
    op.create_index(op.f('ix_workout_exercises_workout_id'), 'workout_exercises', ['workout_id'], unique=False)

    # Water Entries table
    op.create_table(
        'water_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quantity_ml', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_water_entries_id'), 'water_entries', ['id'], unique=False)
    op.create_index(op.f('ix_water_entries_timestamp'), 'water_entries', ['timestamp'], unique=False)
    op.create_index(op.f('ix_water_entries_user_id'), 'water_entries', ['user_id'], unique=False)

    # Sleep Entries table
    op.create_table(
        'sleep_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sleep_start', sa.DateTime(), nullable=False),
        sa.Column('sleep_end', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sleep_entries_id'), 'sleep_entries', ['id'], unique=False)
    op.create_index(op.f('ix_sleep_entries_sleep_start'), 'sleep_entries', ['sleep_start'], unique=False)
    op.create_index(op.f('ix_sleep_entries_user_id'), 'sleep_entries', ['user_id'], unique=False)

    # Food Entries table
    op.create_table(
        'food_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_name', sa.String(length=200), nullable=False),
        sa.Column('meal_category', sa.String(length=50), nullable=False),
        sa.Column('serving_quantity', sa.Float(), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein_g', sa.Float(), nullable=False),
        sa.Column('carbs_g', sa.Float(), nullable=False),
        sa.Column('fat_g', sa.Float(), nullable=False),
        sa.Column('consumed_at', sa.DateTime(), nullable=False),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_entries_consumed_at'), 'food_entries', ['consumed_at'], unique=False)
    op.create_index(op.f('ix_food_entries_id'), 'food_entries', ['id'], unique=False)
    op.create_index(op.f('ix_food_entries_meal_category'), 'food_entries', ['meal_category'], unique=False)
    op.create_index(op.f('ix_food_entries_user_id'), 'food_entries', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('food_entries')
    op.drop_table('sleep_entries')
    op.drop_table('water_entries')
    op.drop_table('workout_exercises')
    op.drop_table('workouts')
    op.drop_table('daily_activities')
    op.drop_table('weight_entries')
    op.drop_table('user_profiles')
    op.drop_table('users')
