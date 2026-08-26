from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.recovery import cases_router, promises_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.system import router as system_router
from app.api.routes.webhook import router as webhook_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(cases_router)
api_router.include_router(dashboard_router)
api_router.include_router(agents_router)
api_router.include_router(simulation_router)
api_router.include_router(promises_router)
api_router.include_router(webhook_router)

__all__ = [
    "api_router",
    "cases_router",
    "promises_router",
    "dashboard_router",
    "agents_router",
    "simulation_router",
    "webhook_router",
    "system_router",
]
