from datetime import datetime

from pydantic import BaseModel, Field

from app.models.promise_to_pay import PromiseStatus


class PromiseToPaySummary(BaseModel):
    """Pydantic summary schema for a Promise-to-Pay record."""

    id: str
    case_id: str
    customer_id: str | None = None
    customer_name: str = "Unknown"
    customer_email: str = "unknown@example.com"
    committed_amount: float = Field(ge=0.0)
    committed_date: datetime
    status: PromiseStatus
    follow_up_count: int = 0
    created_at: datetime
    resolved_at: datetime | None = None


class PromiseListResponse(BaseModel):
    """Response payload for promise listing with status aggregations."""

    items: list[PromiseToPaySummary]
    total: int
    pending_count: int
    kept_count: int
    broken_count: int


class PromiseEvaluationRequest(BaseModel):
    """Request payload to simulate/evaluate a promise resolution."""

    is_paid: bool = Field(
        description="True if payment was received (KEPT), False if broken (BROKEN)"
    )
