# FitTrack REST API Reference

The FitTrack REST API is versioned under `/api/v1`. Interactive OpenAPI documentation and schemas are available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Base URLs
- **Local Development**: `http://localhost:8000/api/v1`
- **Health Check**: `http://localhost:8000/health`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

## Authentication
Authentication uses standard JWT Bearer tokens passed via the `Authorization` header:
```http
Authorization: Bearer <your_jwt_access_token>
```

### 1. User Registration
`POST /api/v1/auth/register`
- **Request Body:**
  ```json
  {
    "name": "Alex Runner",
    "email": "alex@example.com",
    "password": "strongPassword123!"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Alex Runner",
      "email": "alex@example.com",
      "created_at": "2026-10-12T07:30:00Z"
    }
  }
  ```

### 2. User Login
`POST /api/v1/auth/login`
- **Request Body:**
  ```json
  {
    "email": "alex@example.com",
    "password": "strongPassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Alex Runner",
      "email": "alex@example.com",
      "created_at": "2026-10-12T07:30:00Z"
    }
  }
  ```

### 3. Current User Info
`GET /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** User object with embedded profile settings.

---

## Dashboard
### Today's Fitness Summary
`GET /api/v1/dashboard?date=YYYY-MM-DD`
- **Description:** Returns an aggregated overview including current weight, daily step progress, hydration, sleep, calories in/out, recent workouts, weekly trend, and weight progression.
- **Query Parameter:** `date` (optional, defaults to today).

---

## Weight Tracking
### 1. Record Weight
`POST /api/v1/weight`
- **Request Body:**
  ```json
  {
    "weight_kg": 78.5,
    "measurement_date": "2026-10-12",
    "note": "Morning fasted"
  }
  ```
- **Note:** Submitting on an existing date safely updates the day's record without raising duplicate key errors.

### 2. Get Weight History
`GET /api/v1/weight?start_date=2026-09-01&end_date=2026-10-12&limit=50`

### 3. Update Weight Entry
`PATCH /api/v1/weight/{entry_id}`

### 4. Delete Weight Entry
`DELETE /api/v1/weight/{entry_id}` (204 No Content)

---

## Workouts & Exercises
### 1. Create Workout
`POST /api/v1/workouts`
- **Request Body:**
  ```json
  {
    "workout_name": "Push Day Hypertrophy",
    "workout_type": "strength",
    "start_time": "2026-10-12T08:30:00Z",
    "duration_minutes": 50,
    "estimated_calories": 380,
    "notes": "Focused on pause reps",
    "exercises": [
      {
        "exercise_name": "Bench Press",
        "sets": 4,
        "repetitions": 8,
        "weight_used": 80.0
      },
      {
        "exercise_name": "Incline Dumbbell Press",
        "sets": 3,
        "repetitions": 12,
        "weight_used": 26.0
      }
    ]
  }
  ```

### 2. List Workouts
`GET /api/v1/workouts?workout_type=strength&limit=50`

### 3. Get / Update / Delete Workout
`GET /api/v1/workouts/{workout_id}`  
`PATCH /api/v1/workouts/{workout_id}`  
`DELETE /api/v1/workouts/{workout_id}`  

---

## Water & Hydration
### 1. Log Water Intake
`POST /api/v1/water`
- **Request Body:**
  ```json
  {
    "quantity_ml": 250,
    "timestamp": "2026-10-12T10:15:00Z"
  }
  ```

### 2. Daily Water Total
`GET /api/v1/water?date=YYYY-MM-DD`
- **Response:** Total milliliters consumed, target, completion percentage, and individual intake logs.

### 3. Delete Water Entry
`DELETE /api/v1/water/{entry_id}`

---

## Sleep Tracking
### 1. Record Sleep
`POST /api/v1/sleep`
- **Request Body:**
  ```json
  {
    "sleep_start": "2026-10-11T23:00:00Z",
    "sleep_end": "2026-10-12T07:30:00Z",
    "quality_rating": 4
  }
  ```
- **Note:** Accurately calculates duration in minutes across midnight.

### 2. Get Sleep History
`GET /api/v1/sleep?limit=30`

---

## Nutrition & Food Tracking
### 1. Log Food Item
`POST /api/v1/food`
- **Request Body:**
  ```json
  {
    "food_name": "Grilled Chicken Salad",
    "meal_category": "lunch",
    "serving_quantity": 1.0,
    "calories": 420.0,
    "protein_g": 38.0,
    "carbs_g": 18.0,
    "fat_g": 12.0
  }
  ```

### 2. Search Food Database
`GET /api/v1/food/search?q=chicken`
- Integrates with USDA FoodData Central when `USDA_API_KEY` is provided, and includes a rich reference dataset for instant offline results.

---

## Analytics, Reports & Exports
### 1. Weekly & Monthly Summaries
`GET /api/v1/analytics/weekly?date=YYYY-MM-DD`  
`GET /api/v1/analytics/monthly?date=YYYY-MM-DD`  
`GET /api/v1/analytics/weight`  
`GET /api/v1/analytics/workouts`

### 2. Secure CSV Export
`GET /api/v1/analytics/export?data_type=all|weight|workouts|food|activity|water|sleep`
- Downloads an RFC-compliant CSV containing **strictly** the authenticated user's records.

---

## External Integrations & AI
### 1. Exercise Knowledge Base
`GET /api/v1/integrations/exercises?q=squat&muscle_group=Legs`

### 2. Weather Advisory (Open-Meteo)
`GET /api/v1/integrations/weather?lat=40.7128&lon=-74.0060`

### 3. AI Weekly Fitness Insights
`POST /api/v1/insights/weekly?date=YYYY-MM-DD`
- Evaluates real recorded workouts, step activity, sleep duration, and hydration to generate actionable habit guidance.
