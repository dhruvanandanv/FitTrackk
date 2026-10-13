def test_exercise_catalog_integration(client, auth_user):
    headers = auth_user["headers"]

    # Search exercises
    res = client.get("/api/v1/integrations/exercises?q=squat", headers=headers)
    assert res.status_code == 200
    exercises = res.json()
    assert len(exercises) >= 1
    assert any("Squat" in e["name"] for e in exercises)

    # Filter by muscle group
    res_chest = client.get("/api/v1/integrations/exercises?muscle_group=Chest", headers=headers)
    assert res_chest.status_code == 200
    assert all("Chest" in e["muscle_group"] for e in res_chest.json())


def test_nutrition_search_fallback(client, auth_user):
    headers = auth_user["headers"]

    res = client.get("/api/v1/food/search?q=chicken", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert len(data["results"]) >= 1
    first_result = data["results"][0]
    assert "calories" in first_result
    assert "protein_g" in first_result


def test_weather_workout_advisory(client, auth_user):
    headers = auth_user["headers"]

    res = client.get("/api/v1/integrations/weather?lat=40.7128&lon=-74.0060", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "workout_suggestion" in data
    assert "temperature_c" in data


def test_ai_weekly_fitness_insights(client, auth_user):
    headers = auth_user["headers"]

    res = client.post("/api/v1/insights/weekly", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "insights" in data
    assert len(data["insights"]) >= 1
    assert "disclaimer" in data
