from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health check payload."""

    status: str = Field(description="Health status: ok, degraded, or error")
    service: str = Field(description="FastAPI service status")
    database: str = Field(description="Database connectivity status")
    version: str = Field(description="Current application version")
    error: str | None = Field(default=None, description="Error message if degraded")


class RootResponse(BaseModel):
    """Root metadata payload."""

    name: str = Field(description="Project name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Deployment environment")
    docs_url: str = Field(description="OpenAPI interactive documentation path")
    health_url: str = Field(description="Health check probe path")
