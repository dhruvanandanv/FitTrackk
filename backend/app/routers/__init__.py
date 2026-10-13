from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.weight import router as weight_router
from backend.app.routers.activity import router as activity_router
from backend.app.routers.workouts import router as workouts_router
from backend.app.routers.water import router as water_router
from backend.app.routers.sleep import router as sleep_router
from backend.app.routers.food import router as food_router
from backend.app.routers.analytics import router as analytics_router
from backend.app.routers.integrations import router as integrations_router

__all__ = [
    "auth_router",
    "profile_router",
    "dashboard_router",
    "weight_router",
    "activity_router",
    "workouts_router",
    "water_router",
    "sleep_router",
    "food_router",
    "analytics_router",
    "integrations_router",
]
