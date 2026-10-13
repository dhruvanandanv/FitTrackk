def test_user_data_isolation_and_ownership(client, auth_user, other_user):
    headers_user1 = auth_user["headers"]
    headers_user2 = other_user["headers"]

    # 1. User 1 logs a weight entry
    res1 = client.post(
        "/api/v1/weight",
        headers=headers_user1,
        json={"weight_kg": 85.0, "measurement_date": "2026-10-12", "note": "User1 Private Note"},
    )
    assert res1.status_code == 201
    user1_weight_id = res1.json()["id"]

    # 2. User 2 cannot access User 1's weight entry
    res2 = client.get(f"/api/v1/weight/{user1_weight_id}", headers=headers_user2)
    assert res2.status_code == 404

    # 3. User 2 cannot delete User 1's weight entry
    res3 = client.delete(f"/api/v1/weight/{user1_weight_id}", headers=headers_user2)
    assert res3.status_code == 404

    # 4. User 1 logs a workout
    res_w1 = client.post(
        "/api/v1/workouts",
        headers=headers_user1,
        json={
            "workout_name": "User 1 Heavy Leg Day",
            "workout_type": "strength",
            "start_time": "2026-10-12T09:00:00Z",
            "duration_minutes": 50,
            "exercises": [],
        },
    )
    assert res_w1.status_code == 201
    user1_workout_id = res_w1.json()["id"]

    # 5. User 2 cannot access or delete User 1's workout
    res_w2 = client.get(f"/api/v1/workouts/{user1_workout_id}", headers=headers_user2)
    assert res_w2.status_code == 404

    res_w_del = client.delete(f"/api/v1/workouts/{user1_workout_id}", headers=headers_user2)
    assert res_w_del.status_code == 404

    # 6. CSV Export isolation: User 2's export MUST NOT contain User 1's data
    export_res = client.get("/api/v1/analytics/export?data_type=all", headers=headers_user2)
    assert export_res.status_code == 200
    csv_content = export_res.text
    assert "User1 Private Note" not in csv_content
    assert "User 1 Heavy Leg Day" not in csv_content
