import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router, configure_middleware
from app.config import settings
from app.database import Base, engine


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
    Base.metadata.create_all(bind=engine)
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

# Configure Middleware (CORS + Request Logging)
configure_middleware(app)

# Include All API Routers (System, Cases, Dashboard, Agents, Simulation, Promises, Webhooks)
app.include_router(api_router)
