from app.api.dependencies import (
    get_dashboard_service,
    get_promise_service,
    get_recovery_service,
    get_simulation_service,
)
from app.api.middleware import configure_middleware
from app.api.routes import (
    agents_router,
    api_router,
    cases_router,
    dashboard_router,
    promises_router,
    simulation_router,
    system_router,
    webhook_router,
)

# Compatibility aliases
run_router = simulation_router
webhooks_router = webhook_router

__all__ = [
    "api_router",
    "cases_router",
    "promises_router",
    "dashboard_router",
    "agents_router",
    "simulation_router",
    "webhook_router",
    "system_router",
    "run_router",
    "webhooks_router",
    "configure_middleware",
    "get_recovery_service",
    "get_dashboard_service",
    "get_simulation_service",
    "get_promise_service",
]
