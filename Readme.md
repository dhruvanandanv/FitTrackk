# ⚡ FitTrack — Premium Personal Fitness & Wellness Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4+-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-C6FF4D?style=for-the-badge)](LICENSE)

**FitTrack** is a state-of-the-art, responsive personal fitness and wellness tracking web application designed with an Apple Health & modern athletic technology aesthetic. It empowers users to track their daily metrics—weight trajectories, detailed workout sessions, daily steps, calorie and macro nutrition, hydration levels, overnight sleep duration, and multi-dimensional analytics—backed by a production-ready FastAPI backend with strict user data isolation.

---

## 🎨 Visual Design System

FitTrack implements a custom, responsive design system built on CSS custom properties, fluid typography, and dark-mode athletic styling:

### Color Palette
- **Primary Background**: `#090B0A` (Deepest Obsidian)
- **Secondary Background**: `#101310` (Charcoal Canvas)
- **Card Background**: `#151915` (Elevated Container)
- **Elevated Surface**: `#1B201B` (Interactive Surfaces & Floating Modals)
- **Primary Accent**: `#C6FF4D` (High-Energy Lime Green)
- **Secondary Accent**: `#A7E635` (Muted Lime)
- **Primary Text**: `#F5F7F2` (Crisp Chalk White)
- **Secondary Text**: `#A0A79B` (Sage Mist)
- **Muted Text**: `#737B70` (Slate Muted)
- **Borders & Dividers**: `#292F27` (Subtle Dark Slate)
- **Status Indicators**:
  - Success: `#8FE388`
  - Warning: `#FFD166`
  - Error: `#FF7777`
  - Blue / Hydration: `#38bdf8`
  - Purple / Sleep: `#a855f7`

### Typography & Spacing
- **Typography**: Plus Jakarta Sans / Inter with clean sans-serif fallbacks and `tabular-nums` for all dynamic counters and metrics.
- **Spacing Scale**: 4px / 8px baseline rhythm (`--space-xs` through `--space-3xl`).
- **Touch Targets**: Minimum 44px clickable areas on all mobile inputs, buttons, and navigation destinations.

---

## 📱 Responsive & Cross-Device Engineering

FitTrack was crafted from the ground up for zero-compromise cross-device operation:

| Viewport Category | Target Devices & Screen Widths | Layout Adaptation |
|:---|:---|:---|
| **Desktop / Ultrawide** | 1280px, 1440px, 1920px+ | Fixed 260px collapsible sidebar, 6-card KPI grid, dual-column analytics charts, expansive workout logs. |
| **Laptop / Tablet** | 768px, 1024px | Dynamic 2-column or 3-column metric grid, collapsible drawers, responsive Chart.js auto-resizing. |
| **Standard Mobile** | 375px, 390px, 414px, 430px (iPhone & Android) | Desktop sidebar hides; sticky bottom navigation bar (5 destinations) + slide-up More drawer; touch-friendly cards. |
| **Small Mobile** | 320px, 360px (SE, mini, compact devices) | Single-column fluid layout with `min-width: 0` constraints, fluid typography via `clamp()`, and guaranteed **0 horizontal overflow**. |

---

## 🚀 Key Features

### 1. Unified Showcase Dashboard
- **Personalized Header**: Dynamic greeting, current date, live weather advisory pill (via Open-Meteo), and quick-action trigger.
- **6 Core Health KPI Cards**:
  1. *Current Weight*: Latest reading, unit, and progress indicator.
  2. *Daily Steps*: Real-time progress bar toward the 10,000-step target.
  3. *Calories*: Intake vs. active burn summary.
  4. *Hydration*: Daily water total with direct quick-add action.
  5. *Sleep Duration*: Last recorded sleep duration and target completion.
  6. *Workout Status*: Total weekly workouts and duration summary.
- **Interactive Visualizations**:
  - 7-Day Activity & Step Chart (lime-accented Bar/Line Chart).
  - Weight Progress Line Chart with hover tooltips and dynamic date axes.
- **6 Instant Quick Actions**: Log Weight, Log Workout, Update Steps, Record Food, +250ml Water, and Record Sleep.

### 2. Dedicated Weight Tracking
- Real-time BMI calculation based on stored profile height.
- Progress summary comparing current weight against user-defined target weight.
- Historical weight progression chart with interactive tooltips.
- Add-weight form with measurement date picker.
- Complete measurement history table with inline delete actions.

### 3. Workout Tracking & Exercise Builder
- Support for multiple training categories (Strength, Cardio, HIIT, Mobility).
- Multi-exercise set-and-rep builder (exercise name, sets, repetitions, weight/resistance, duration, distance, and notes).
- Chronological workout timeline displaying exercise chips and calculated volume.
- Inline workout deletion with immediate state refresh.

### 4. Activity & Step Counter
- Dedicated daily activity logger for steps, active minutes, and cardio minutes.
- Estimated calories burned calculation.
- 7-day activity history log table.

### 5. Nutrition & Calorie Tracker
- Daily calorie and macronutrient breakdown (Protein, Carbohydrates, Fats).
- Interactive Macro Distribution Doughnut Chart.
- Food search powered by USDA FoodData Central integration with seamless offline fallback dataset.
- Meal categorization (Breakfast, Lunch, Dinner, Snack).

### 6. Hydration Tracker
- Dynamic visual water bottle fill animation that updates reactively upon every intake.
- Quick-add buttons (`+250 ml`, `+500 ml`, `+750 ml`) for instantaneous one-tap logging.
- Custom milliliter input for precise hydration recording.
- Chronological log of today's water entries with single-click delete.

### 7. Sleep Tracking
- Start time and wake time logger with accurate handling of overnight sleep sessions (e.g. 23:00 to 07:00).
- Sleep quality selector (Poor, Fair, Good, Excellent).
- 7-day sleep log history.

### 8. Multi-Dimensional Analytics
- 30-day comprehensive weight trajectory chart.
- Weekly workout frequency and duration trends.
- Nutrition and hydration consistency metrics.
- Algorithmic AI fitness insights generated from genuine user activity data.
- RFC-compliant CSV export for offsite backups and personal records.

### 9. User Profile & Settings
- Height, weight, target weight, daily step goal, water target, and sleep target configuration.
- Measurement unit toggle (Metric kg/cm vs. Imperial lbs/in).
- Secure account details and logout action.

---

## 🛠️ Architecture & Tech Stack

```
fittrack/
├── backend/
│   ├── app/
│   │   ├── config.py             # Pydantic Settings & environment variables
│   │   ├── database.py           # SQLAlchemy 2.0 Engine & sessionmaker
│   │   ├── main.py               # FastAPI app factory, CORS, static mounts
│   │   ├── models/               # Declarative ORM models (User, Weight, Workout, etc.)
│   │   ├── routers/              # Modular API routes mounted at /api/v1
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   └── services/             # Domain logic (Auth, Dashboard, Analytics, USDA, Weather)
│   └── tests/                    # Pytest suite with 19 comprehensive test cases
├── frontend/
│   ├── index.html                # Semantic HTML5 single-page application structure
│   ├── style.css                 # Custom CSS design system, dark palette, responsive media queries
│   ├── script.js                 # Unified frontend router, state store, UI handlers
│   ├── api.js                    # Authenticated Fetch API client with JWT interception
│   └── auth.js                   # Session lifecycle, token storage, user profiles
├── alembic/                      # Database migration scripts
├── docs/                         # In-depth architectural, API, and deployment documentation
├── Dockerfile                    # Container definition for production deployment
├── docker-compose.yml            # Multi-container orchestration (FastAPI + PostgreSQL)
└── requirements.txt              # Strict Python dependencies
```

---

## 💻 Local Setup & Development

### 1. Prerequisites
- Python 3.11+
- Node.js (optional, for linting/verification)

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/fittrack.git
cd fittrack

# Create and activate a virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration uses local SQLite:
```ini
PROJECT_NAME="FitTrack"
ENVIRONMENT="development"
SECRET_KEY="dev-secret-key-change-in-production"
DATABASE_URL="sqlite:///./fittrack.db"
CORS_ORIGINS=["http://localhost:8000","http://127.0.0.1:8000"]
```

### 4. Run Database Migrations
```bash
alembic upgrade head
```

### 5. Launch the Application
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
- **Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Tests

The test suite runs with `pytest` using an isolated in-memory/file test database:
```bash
pytest -v
```
All **21/21** tests cover:
- Authentication, registration, and duplicate email prevention.
- Production security configuration validator (enforces random keys, prevents dev fallbacks and SQLite in production).
- Static frontend index and asset delivery.
- Weight CRUD, historical metrics, and BMI calculation.
- Workout CRUD with multi-exercise set-and-rep structures.
- Water logging and daily total aggregation.
- Overnight sleep duration calculation.
- Food nutrition totals and macro breakdown.
- Dashboard aggregated health summaries.
- External integration fallbacks (USDA FoodData, Open-Meteo, AI insights).
- Strict cross-user data isolation and ownership enforcement.

---

## 🌐 Cloud Production Deployment

FitTrack is optimized for **Render** (Web Application), **Neon** (Managed Serverless PostgreSQL), and **GitHub** (Source Control).

### 1. Neon Managed PostgreSQL Setup
1. Create a free project on [neon.tech](https://neon.tech).
2. Copy the connection URI:
   ```
   postgresql://user:password@ep-name.region.aws.neon.tech/neondb?sslmode=require
   ```
3. FitTrack automatically normalizes `postgres://` to `postgresql://` and enables connection pooling (`pool_pre_ping=True`, `pool_recycle=300`) to gracefully handle serverless sleep states.

### 2. Render Deployment (1-Click Blueprint)
The repository includes a [render.yaml](file:///e:/FITTRACK/fittrack/render.yaml) blueprint:
1. In Render, select **Blueprints** -> **New Blueprint Instance**.
2. Connect your GitHub repository.
3. Supply `DATABASE_URL` with your Neon connection string.
4. Render automatically provisions the service, runs `alembic upgrade head`, and launches the application.

### 3. Render Manual Configuration (Python Web Service)
- **Runtime**: `Python 3`
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`
- **Required Environment Variables**:
  - `ENVIRONMENT=production`
  - `DATABASE_URL=<your-neon-connection-string>`
  - `SECRET_KEY=<32-char-random-secret>`
  - `JWT_SECRET_KEY=<32-char-random-secret>`
  - `CORS_ORIGINS=*` (or your Render URL)

Detailed instructions, Docker options, and troubleshooting steps can be found in the [Deployment Guide](file:///e:/FITTRACK/fittrack/docs/DEPLOYMENT.md).

---

## 📄 License
This project is open-source and distributed under the [MIT License](LICENSE).
