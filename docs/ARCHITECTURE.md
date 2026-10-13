# FitTrack Architecture & Design Documentation

## 1. High-Level Architecture

FitTrack follows a clean, decoupled, layered web application architecture:

```
[ Frontend: HTML5 / CSS3 / Vanilla JS ES Modules / Chart.js ]
                             │
                             ▼  (JSON REST via Fetch API / Bearer JWT)
[ FastAPI Application Layer: Routers + Dependencies + Lifespan ]
                             │
                             ▼
[ Business Logic & Services Layer: Aggregations, Metrics, Weather, AI Insights ]
                             │
                             ▼
[ Data Access Layer: SQLAlchemy 2.0 ORM + Alembic Migrations ]
                             │
                             ▼
[ Relational Persistence: PostgreSQL (Prod) / SQLite (Local Dev & Testing) ]
```

---

## 2. Layer Responsibilities

### Frontend Layer (`frontend/`)
- Pure client-side web application built with modern ES Modules and zero heavyweight build tooling requirements.
- Responsive, dark-themed UI styled with a curated design system (neon-lime accent, charcoal surface layers, glassmorphism cards).
- Visual charts powered by Chart.js (interactive line, bar, and doughnut visualizations).
- `api.js`: Unified authenticated HTTP client managing token headers, error normalization, and CSV download handling.
- `auth.js`: Session lifecycle, profile cache, and automatic session expiration handling.

### Presentation & Routing Layer (`backend/app/routers/`)
- FastAPI versioned APIRouter modules mounted under `/api/v1`.
- Fast, strict request/response validation using Pydantic V2 schemas.
- Dependency injection handles database sessions (`get_db`) and user identity resolution (`get_current_user`).

### Domain Services Layer (`backend/app/services/`)
- Decouples route handlers from database queries and external integrations.
- **`AuthService`**: Password hashing with Argon2, user account provisioning, JWT issuance.
- **`DashboardService`**: Aggregates daily steps, hydration, sleep, weight trends, and activity into a single round-trip payload.
- **`AnalyticsService`**: Calculates weekly/monthly consistency percentages, moving averages, and weight trajectories.
- **`NutritionService`**: Interfaces with USDA FoodData Central with an offline fallback dataset.
- **`ExerciseService`**: Searchable catalog of muscle groups, instructions, and standard training movements.
- **`WeatherService`**: Consumes Open-Meteo REST API to supply outdoor training suggestions.
- **`AIInsightsService`**: Algorithmic fitness analysis grounded in actual user data.
- **`ExportService`**: RFC-compliant CSV generation with strict user isolation.

### Persistence Layer (`backend/app/models/` & `alembic/`)
- SQLAlchemy 2.0 declarative models with foreign key constraints, cascade deletions, and composite unique indices.
- Alembic migration scripts guarantee safe schema lifecycle management in CI/CD and production environments.

---

## 3. Database Schema Entity Relationship

```
User (id, email, password_hash, name)
 ├── 1:1 ── UserProfile (fitness_goal, targets, height, units)
 ├── 1:N ── WeightEntry (weight_kg, measurement_date) [Unique per user+date]
 ├── 1:N ── DailyActivity (steps, active_minutes, calories_burned) [Unique per user+date]
 ├── 1:N ── Workout (name, type, duration_minutes, start_time)
 │            └── 1:N ── WorkoutExercise (name, sets, reps, weight_used)
 ├── 1:N ── WaterEntry (quantity_ml, timestamp)
 ├── 1:N ── SleepEntry (sleep_start, sleep_end, duration_minutes, quality)
 └── 1:N ── FoodEntry (food_name, meal_category, calories, protein, carbs, fat)
```

---

## 4. Security Principles
1. **Password Protection**: Passwords are never stored in plaintext. Passwords are salted and hashed using **Argon2** via `argon2-cffi`.
2. **Stateless Authentication**: Verified with JSON Web Tokens (JWT) signed with HMAC-SHA256 using server-held secret keys.
3. **Data Isolation & Ownership**: Route handlers derive ownership strictly from the authenticated JWT subject (`current_user.id`). User IDs provided in payloads or query parameters are never trusted to grant data access.
4. **CORS Restrictions**: Configured via environment variables to allow only designated origins in production.
