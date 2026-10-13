from datetime import date, datetime, timedelta, timezone


def test_weight_crud_and_calculations(client, auth_user):
    headers = auth_user["headers"]

    # 1. Create weight entry
    res = client.post(
        "/api/v1/weight",
        headers=headers,
        json={"weight_kg": 80.5, "measurement_date": "2026-10-01", "note": "Baseline"},
    )
    assert res.status_code == 201
    entry_id = res.json()["id"]
    assert res.json()["weight_kg"] == 80.5

    # 2. Get history
    res = client.get("/api/v1/weight", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 3. Update entry
    res = client.patch(
        f"/api/v1/weight/{entry_id}",
        headers=headers,
        json={"weight_kg": 80.0, "note": "Adjusted"},
    )
    assert res.status_code == 200
    assert res.json()["weight_kg"] == 80.0

    # 4. Upsert on same date updates measurement without throwing duplicate constraint error
    res = client.post(
        "/api/v1/weight",
        headers=headers,
        json={"weight_kg": 79.8, "measurement_date": "2026-10-01", "note": "Updated weigh-in"},
    )
    assert res.status_code == 201
    assert res.json()["weight_kg"] == 79.8

    # 5. Delete entry
    res = client.delete(f"/api/v1/weight/{entry_id}", headers=headers)
    assert res.status_code == 204


def test_workout_crud_with_exercises(client, auth_user):
    headers = auth_user["headers"]

    payload = {
        "workout_name": "Full Body Hypertrophy",
        "workout_type": "strength",
        "start_time": "2026-10-10T10:00:00Z",
        "duration_minutes": 60,
        "notes": "Solid pump",
        "estimated_calories": 420.0,
        "exercises": [
            {
                "exercise_name": "Barbell Squats",
                "sets": 4,
                "repetitions": 8,
                "weight_used": 100.0,
            },
            {
                "exercise_name": "Bench Press",
                "sets": 3,
                "repetitions": 10,
                "weight_used": 80.0,
            },
        ],
    }

    # 1. Create Workout
    res = client.post("/api/v1/workouts", headers=headers, json=payload)
    assert res.status_code == 201
    workout = res.json()
    assert workout["workout_name"] == "Full Body Hypertrophy"
    assert len(workout["exercises"]) == 2
    workout_id = workout["id"]

    # 2. Get Workout by ID
    res = client.get(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["duration_minutes"] == 60

    # 3. Filter by type
    res = client.get("/api/v1/workouts?workout_type=strength", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 4. Delete Workout
    res = client.delete(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert res.status_code == 204


def test_water_logging_and_daily_total(client, auth_user):
    headers = auth_user["headers"]
    today_str = date.today().isoformat()

    # Log 250ml
    res = client.post("/api/v1/water", headers=headers, json={"quantity_ml": 250})
    assert res.status_code == 201
    water_id = res.json()["id"]

    # Log 500ml
    client.post("/api/v1/water", headers=headers, json={"quantity_ml": 500})

    # Get Daily Water summary
    res = client.get(f"/api/v1/water?date={today_str}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_ml"] >= 750
    assert data["percentage"] > 0

    # Delete entry
    res = client.delete(f"/api/v1/water/{water_id}", headers=headers)
    assert res.status_code == 204


def test_sleep_overnight_duration_calculation(client, auth_user):
    headers = auth_user["headers"]

    # Sleep from 23:00 to 07:30 next morning (8.5 hours = 510 minutes)
    payload = {
        "sleep_start": "2026-10-10T23:00:00Z",
        "sleep_end": "2026-10-11T07:30:00Z",
        "quality_rating": 5,
        "data_source": "manual",
    }
    res = client.post("/api/v1/sleep", headers=headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["duration_minutes"] == 510


def test_food_nutrition_totals(client, auth_user):
    headers = auth_user["headers"]
    today_str = date.today().isoformat()

    # 1. Log Breakfast
    client.post(
        "/api/v1/food",
        headers=headers,
        json={
            "food_name": "Oatmeal with Protein",
            "meal_category": "breakfast",
            "serving_quantity": 1.0,
            "calories": 400.0,
            "protein_g": 30.0,
            "carbs_g": 55.0,
            "fat_g": 6.0,
        },
    )

    # 2. Log Lunch
    client.post(
        "/api/v1/food",
        headers=headers,
        json={
            "food_name": "Chicken Breast with Rice",
            "meal_category": "lunch",
            "serving_quantity": 1.0,
            "calories": 500.0,
            "protein_g": 45.0,
            "carbs_g": 50.0,
            "fat_g": 10.0,
        },
    )

    # 3. Get Day Food Summary
    res = client.get(f"/api/v1/food?date={today_str}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_calories"] >= 900.0
    assert data["total_protein_g"] >= 75.0
    assert len(data["entries"]) >= 2


def test_dashboard_aggregated_summary(client, auth_user):
    headers = auth_user["headers"]
    today_str = date.today().isoformat()

    res = client.get(f"/api/v1/dashboard?date={today_str}", headers=headers)
    assert res.status_code == 200
    data = response_json = res.json()
    assert "steps" in data
    assert "water" in data
    assert "sleep" in data
    assert "weekly_activity_trend" in data
    assert "weight_trend" in data


def test_invalid_input_validation(client, auth_user):
    headers = auth_user["headers"]

    # Invalid weight (must be > 15 kg)
    res = client.post(
        "/api/v1/weight",
        headers=headers,
        json={"weight_kg": -10.0, "measurement_date": "2026-10-10"},
    )
    assert res.status_code == 422

    # Invalid meal category
    res = client.post(
        "/api/v1/food",
        headers=headers,
        json={
            "food_name": "Test",
            "meal_category": "invalid_meal_type",
            "calories": 100,
        },
    )
    assert res.status_code == 422
