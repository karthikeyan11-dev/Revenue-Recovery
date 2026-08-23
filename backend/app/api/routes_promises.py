import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.promise_to_pay import PromiseStatus
from app.schemas.promise import (
    PromiseEvaluationRequest,
    PromiseListResponse,
    PromiseToPaySummary,
)
from app.services.promise_service import PromiseTrackerService

logger = logging.getLogger("app.api.promises")
router = APIRouter(prefix="/promises", tags=["Promise to Pay"])


@router.get(
    "",
    response_model=PromiseListResponse,
    summary="List all tracked promises to pay",
    operation_id="list_promises",
)
def list_promises(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: PromiseStatus | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PromiseListResponse:
    """Retrieve paginated list of Promise-to-Pay records with aggregation counts."""
    service = PromiseTrackerService(db)
    return service.list_promises(limit=limit, offset=offset, status=status)


@router.post(
    "/{promise_id}/evaluate",
    response_model=PromiseToPaySummary,
    summary="Evaluate a promise as KEPT or BROKEN",
    operation_id="evaluate_promise",
)
def evaluate_promise(
    promise_id: str,
    payload: PromiseEvaluationRequest,
    db: Session = Depends(get_db),
) -> PromiseToPaySummary:
    """
    Evaluates a pending payment promise.
    - If KEPT (is_paid=True): Marks promise kept and completes case recovery.
    - If BROKEN (is_paid=False): Re-invokes Strategist for exactly 1 follow-up, or forces human escalation if already followed up.
    """
    service = PromiseTrackerService(db)
    try:
        promise, case = service.evaluate_promise(promise_id=promise_id, is_paid=payload.is_paid)
        cust = case.customer if case else None
        return PromiseToPaySummary(
            id=promise.id,
            case_id=promise.case_id,
            customer_id=cust.id if cust else None,
            customer_name=cust.name if cust else "Unknown",
            customer_email=cust.email if cust else "unknown@example.com",
            customer_segment=cust.segment.value if cust and cust.segment else "REGULAR",
            committed_amount=promise.committed_amount,
            committed_date=promise.committed_date,
            status=promise.status,
            follow_up_count=promise.follow_up_count,
            created_at=promise.created_at,
            resolved_at=promise.resolved_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error evaluating promise {promise_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Promise evaluation failed: {e}") from e
