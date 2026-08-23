import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import (
    agents_router,
    cases_router,
    dashboard_router,
    promises_router,
    run_router,
    webhooks_router,
)
from app.config import settings
from app.db import Base, check_db_connection, engine
from app.schemas.system import HealthResponse, RootResponse


# Structured Logging Setup
def setup_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown hooks."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    logger.info(f"Configured LLM Provider: {settings.LLM_PROVIDER} | Model: {settings.MODEL}")
    settings.validate_llm_config()
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            # Transaction columns
            conn.execute(
                text(
                    "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS razorpay_order_id VARCHAR(64)"
                )
            )
            # PaymentFailure columns
            conn.execute(
                text(
                    "ALTER TABLE payment_failures ADD COLUMN IF NOT EXISTS raw_error_source VARCHAR(64)"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE payment_failures ADD COLUMN IF NOT EXISTS raw_error_step VARCHAR(64)"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE payment_failures ADD COLUMN IF NOT EXISTS raw_error_reason VARCHAR(64)"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE payment_failures ADD COLUMN IF NOT EXISTS razorpay_payment_id VARCHAR(64)"
                )
            )
            # AuditLog columns
            conn.execute(
                text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS empirical_confidence FLOAT")
            )
            conn.execute(
                text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS llm_stated_confidence FLOAT")
            )
            conn.execute(
                text(
                    "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS precedent_sample_size INTEGER"
                )
            )
            # RecoveryCase columns
            conn.execute(
                text("ALTER TABLE recovery_cases ADD COLUMN IF NOT EXISTS precedent_count INTEGER")
            )
            conn.execute(
                text(
                    "ALTER TABLE recovery_cases ADD COLUMN IF NOT EXISTS empirical_confidence FLOAT"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE recovery_cases ADD COLUMN IF NOT EXISTS playbook_precedents_json TEXT"
                )
            )
            # RecoveryAction columns
            conn.execute(
                text(
                    "ALTER TABLE recovery_actions ADD COLUMN IF NOT EXISTS empirical_confidence FLOAT"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE recovery_actions ADD COLUMN IF NOT EXISTS llm_stated_confidence FLOAT"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE recovery_actions ADD COLUMN IF NOT EXISTS precedent_sample_size INTEGER"
                )
            )
            conn.commit()
        logger.info("Database schemas and all columns verified and synchronized.")
    except Exception as e:
        logger.warning(f"Database schema sync warning: {e}")
    yield
    logger.info("Shutting down Application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous, policy-governed AI Revenue Recovery Orchestrator backend REST API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Feature Routers
app.include_router(cases_router)
app.include_router(dashboard_router)
app.include_router(agents_router)
app.include_router(run_router)
app.include_router(promises_router)
app.include_router(webhooks_router)


@app.get(
    "/",
    response_model=RootResponse,
    tags=["System"],
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


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
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
