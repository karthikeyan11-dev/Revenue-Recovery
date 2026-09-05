import logging

from fastapi import APIRouter

from app.config import settings
from app.database import check_db_connection
from app.schemas.system import HealthResponse, RootResponse

logger = logging.getLogger("app.api.routes.system")
router = APIRouter(tags=["System"])


@router.get(
    "/",
    response_model=RootResponse,
    summary="Root metadata endpoint",
    operation_id="get_root",
)
def root() -> RootResponse:
    """Root metadata endpoint."""
    return RootResponse(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        docs_url="/docs",
        health_url="/health",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health and database connectivity probe",
    operation_id="get_health",
)
def health_check() -> HealthResponse:
    """
    Health check endpoint verifying system status and database connectivity.
    Returns 200 with component statuses (service=online, database=connected/unreachable).
    """
    db_ok, db_message = check_db_connection()

    if not db_ok:
        logger.warning(f"Health check: database connectivity degraded ({db_message})")
        return HealthResponse(
            status="degraded",
            service="online",
            database="unreachable",
            version=settings.VERSION,
            error=db_message,
        )

    return HealthResponse(
        status="ok",
        service="online",
        database="connected",
        version=settings.VERSION,
    )
