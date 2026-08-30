import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger("app.api.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP request method, path, and duration."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            f"{request.method} {request.url.path} - HTTP {response.status_code} ({process_time_ms:.2f}ms)"
        )
        return response


def configure_middleware(app: FastAPI) -> None:
    """Configures CORS and request logging middleware on the FastAPI instance."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
