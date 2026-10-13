# 🚀 FitTrack Production Deployment Guide (Render + Neon + GitHub)

This guide provides end-to-end instructions for deploying the **FitTrack** application to production using **Render** for web application hosting, **Neon** for managed serverless PostgreSQL, and **GitHub** for source control.

---

## 1. High-Level Production Architecture

```
                    ┌────────────────────────────────────────┐
                    │               CLIENTS                  │
                    │  Desktop / Laptop / iPhone / Android   │
                    └──────────────────┬─────────────────────┘
                                       │ HTTPS (Port 443)
                                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        RENDER WEB SERVICE                              │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                    FastAPI Application Server                  │   │
│   │                                                                │   │
│   │  Static UI Mount:        API Endpoints (/api/v1):              │   │
│   │  /static/style.css       /auth, /dashboard, /weight,           │   │
│   │  /static/script.js       /workouts, /activity, /food,          │   │
│   │  / -> index.html         /water, /sleep, /analytics            │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
└───────────────────────────────────┼────────────────────────────────────┘
                                    │ TLS 1.3 / sslmode=require
                                    │ Pooled SQLAlchemy Sessions
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  NEON MANAGED POSTGRESQL (CLOUD)                       │
│                                                                        │
│   Database: neondb                                                     │
│   Tables: users, user_profiles, weight_entries, workouts, exercises,  │
│           daily_activities, water_entries, sleep_entries, food_entries │
│   Version Control: alembic_version                                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites

Before beginning deployment, ensure you have:
1. A **GitHub** account ([github.com](https://github.com)).
2. A **Render** account ([render.com](https://render.com)).
3. A **Neon** account ([neon.tech](https://neon.tech)).
4. Python 3.11+ installed locally.

---

## 3. Step 1: Provision Managed PostgreSQL on Neon

1. Log in to [Neon Console](https://console.neon.tech).
2. Click **Create Project**:
   - **Project Name**: `fittrack-db`
   - **Postgres Version**: `16` (Default)
   - **Region**: Select the region closest to your target Render region (e.g., *US East (Ohio / N. Virginia)* or *US West (Oregon)*).
3. Once the database is created, navigate to **Dashboard** -> **Connection Details**:
   - In the dropdown, ensure **neondb** is selected.
   - Choose **Pooled connection** (recommended for web applications) or **Direct connection**.
   - Copy the connection string. It will look similar to:
     ```
     postgresql://neondb_owner:npg_AbCdEf123456@ep-cool-cloud-a5xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
   *(Note: If the copied URL begins with `postgres://`, FitTrack automatically normalizes it to `postgresql://` and ensures `sslmode=require` is present).*

---

## 4. Step 2: Push Repository to GitHub

If your project is not yet in a GitHub repository:

1. **Initialize Git & Verify Exclusions**:
   Ensure `.gitignore` and `.dockerignore` prevent committing local files (`.env`, `venv/`, `*.db`):
   ```bash
   git init
   git add .
   git commit -m "feat: production-ready FitTrack application"
   ```

2. **Create a Private or Public GitHub Repository**:
   - Go to [github.com/new](https://github.com/new).
   - Name your repository (e.g. `fittrack`).
   - Do NOT initialize with a README (one already exists).

3. **Link and Push**:
   ```bash
   git remote add origin https://github.com/<your-username>/fittrack.git
   git branch -M main
   git push -u origin main
   ```

---

## 5. Step 3: Deploy to Render

You can deploy using either **Render Blueprints (Automated 1-Click)** or **Manual Web Service Setup**.

### Option A: 1-Click Blueprint (Recommended)
FitTrack includes a pre-configured `render.yaml` specification:

1. In Render, go to **Blueprints** -> **New Blueprint Instance**.
2. Connect your `fittrack` repository.
3. Render will detect `render.yaml`.
4. Under **Environment Variables**:
   - Set `DATABASE_URL` to your Neon PostgreSQL connection string.
   - `SECRET_KEY` and `JWT_SECRET_KEY` will be automatically generated with cryptographically secure values.
5. Click **Apply**. Render will provision and launch the service.

---

### Option B: Manual Web Service Setup (Native Python)

1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your `fittrack` repository.
3. Configure the settings:
   - **Name**: `fittrack`
   - **Region**: Same region as your Neon database (e.g., *Oregon* or *Ohio*).
   - **Branch**: `main`
   - **Root Directory**: Leave blank (uses repository root).
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free` (or Starter for higher memory).

4. **Add Environment Variables** (Under **Advanced** -> **Environment Variables**):

| Key | Value | Description |
|:---|:---|:---|
| `ENVIRONMENT` | `production` | Enables strict security checks (disables dev secrets). |
| `DATABASE_URL` | `postgresql://...neon.tech/neondb?sslmode=require` | Your Neon PostgreSQL connection string. |
| `SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | Minimum 32-character encryption key. |
| `JWT_SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | JWT signing key. |
| `CORS_ORIGINS` | `*` or `https://<your-render-subdomain>.onrender.com` | Allowed CORS origins. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Session lifetime (7 days). |
| `PYTHON_VERSION` | `3.11.9` | Python runtime version. |

5. **Configure Health Check**:
   - Scroll down to **Health Check Path** and set it to:
     ```
     /health
     ```
6. Click **Create Web Service**.

---

### Option C: Docker Deployment on Render

If deploying using Docker on Render:
1. Select **Docker** as the runtime.
2. Render will automatically build using [Dockerfile](file:///e:/FITTRACK/fittrack/Dockerfile).
3. The Dockerfile automatically runs `alembic upgrade head` on startup before launching Uvicorn on `${PORT}`.
4. Supply the same environment variables listed in the table above.

---

## 6. Step 4: Running Database Migrations

### Automated Migrations (Standard)
During the build command (`alembic upgrade head`) or Docker startup, Alembic automatically inspects your Neon database:
1. Creates the `alembic_version` metadata tracking table.
2. Applies `001_initial_schema` to create all 8 core tables with indexes, foreign keys, and unique constraints.

### Manual Migrations (From Local Terminal)
If you ever need to apply migrations directly to Neon from your developer machine:
```bash
# On Windows PowerShell:
$env:DATABASE_URL="postgresql://user:pass@ep-name.region.aws.neon.tech/neondb?sslmode=require"
.\venv\Scripts\alembic upgrade head

# On macOS / Linux:
DATABASE_URL="postgresql://user:pass@ep-name.region.aws.neon.tech/neondb?sslmode=require" alembic upgrade head
```

To verify the current migration head on Neon:
```bash
alembic current
```

---

## 7. Step 5: Post-Deployment Verification

Once Render displays **Deploy live**:

### 1. Probe the Production Health Endpoint
```bash
curl -f https://<your-render-subdomain>.onrender.com/health
```
Expected JSON Response:
```json
{
  "status": "healthy",
  "service": "fittrack-backend",
  "version": "1.0.0",
  "environment": "production",
  "database": "healthy",
  "timestamp": "2026-10-12T09:00:00.000000+00:00"
}
```
*Note: If `"database"` returns `"unreachable"`, verify your `DATABASE_URL` credentials in Render.*

### 2. Desktop & Mobile Browser Verification
1. Open `https://<your-render-subdomain>.onrender.com/` on your laptop/desktop.
2. Register a new user account (e.g. `athlete@example.com`).
3. Log a weight entry (e.g. `74.5 kg`).
4. Log a workout with exercise sets and reps.
5. Tap `+250ml` water and watch the water bottle graphic fill.
6. Refresh the page to confirm that data persists from Neon PostgreSQL.
7. Open the same URL on your iPhone or Android phone:
   - Verify the desktop sidebar is hidden.
   - Confirm the fixed 5-item bottom navigation bar appears.
   - Tap **More** to open the slide-up drawer and access Nutrition, Hydration, Sleep, and Analytics.
   - Confirm zero horizontal scrolling.

---

## 8. Troubleshooting Guide

### 1. Neon Serverless Cold Starts / Connection Dropped
- **Symptom**: `SSL SYSCALL error: EOF detected` or `connection closed unexpectedly`.
- **Cause**: Neon serverless compute suspends after 5 minutes of inactivity on free tier.
- **Solution**: FitTrack has built-in connection resiliency configured in `backend/app/database.py`:
  - `pool_pre_ping=True`: Tests connection liveness before every query.
  - `pool_recycle=300`: Refreshes connections every 5 minutes.
  - If a connection dropped while idle, SQLAlchemy automatically discards it and reconnects.

### 2. Render Deployment Timeout / Port Binding
- **Symptom**: Render logs show `Port scan timeout: service failed to bind to 0.0.0.0:$PORT`.
- **Cause**: Hardcoded port in startup command.
- **Solution**: Ensure your start command binds to `$PORT`:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### 3. Application Fails to Start with `CRITICAL SECURITY CONFIGURATION`
- **Symptom**: Startup crashes with `ValueError: In production mode, SECRET_KEY must be set to a secure string...`.
- **Cause**: FitTrack's security validator prevents running with default development keys in production.
- **Solution**: Set `SECRET_KEY` in Render environment variables to a random 32+ character string (`openssl rand -hex 32`).

### 4. CORS Errors on Cross-Origin Frontend
- **Symptom**: Browser console logs `Access-Control-Allow-Origin header missing`.
- **Solution**: If hosting the frontend on a separate domain (e.g. Vercel), add that domain to `CORS_ORIGINS` in Render:
  ```
  CORS_ORIGINS=https://your-frontend.vercel.app,https://your-backend.onrender.com
  ```
