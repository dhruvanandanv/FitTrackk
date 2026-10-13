from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import (
    auth_router,
    profile_router,
    dashboard_router,
    weight_router,
    activity_router,
    workouts_router,
    water_router,
    sleep_router,
    food_router,
    analytics_router,
    integrations_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade personal fitness tracker API with real database persistence, analytics, and integrations.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    db_status = "healthy"
    try:
        from backend.app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "fittrack-backend",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Include versioned API routers under /api/v1
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(profile_router, prefix=api_v1_prefix)
app.include_router(dashboard_router, prefix=api_v1_prefix)
app.include_router(weight_router, prefix=api_v1_prefix)
app.include_router(activity_router, prefix=api_v1_prefix)
app.include_router(workouts_router, prefix=api_v1_prefix)
app.include_router(water_router, prefix=api_v1_prefix)
app.include_router(sleep_router, prefix=api_v1_prefix)
app.include_router(food_router, prefix=api_v1_prefix)
app.include_router(analytics_router, prefix=api_v1_prefix)
app.include_router(integrations_router, prefix=api_v1_prefix)

# Frontend Static Serving
base_dir = Path(__file__).resolve().parent.parent.parent
frontend_dir = base_dir / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "FitTrack API is running. Visit /docs for OpenAPI documentation."}

    @app.get("/login", include_in_schema=False)
    def serve_login():
        login_file = frontend_dir / "login.html"
        if login_file.exists():
            return FileResponse(str(login_file))
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/register", include_in_schema=False)
    def serve_register():
        reg_file = frontend_dir / "register.html"
        if reg_file.exists():
            return FileResponse(str(reg_file))
        return FileResponse(str(frontend_dir / "index.html"))
