import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.promise_to_pay import PromiseStatus
from app.models.recovery_case import CaseStatus
from app.schemas.promise import (
    PromiseEvaluationRequest,
    PromiseListResponse,
    PromiseToPaySummary,
)
from app.schemas.recovery import CasesListResponse, RecoveryCaseDetail
from app.services.promise_service import PromiseTrackerService
from app.services.recovery_orchestrator import RecoveryOrchestratorService

logger = logging.getLogger("app.api.routes.recovery")

cases_router = APIRouter(prefix="/cases", tags=["Recovery Cases"])
promises_router = APIRouter(prefix="/promises", tags=["Promise to Pay"])


# --- Cases Endpoints ---
@cases_router.get(
    "",
    response_model=CasesListResponse,
    summary="List recovery cases with filtering and pagination",
    operation_id="list_recovery_cases",
)
def list_cases(
    status_filter: CaseStatus | None = Query(
        None, alias="status", description="Filter by case status"
    ),
    priority: str | None = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    search: str | None = Query(None, description="Search by Case ID, Customer name, or email"),
    date_from: datetime | None = Query(
        None, description="Filter cases created on or after this timestamp"
    ),
    date_to: datetime | None = Query(
        None, description="Filter cases created on or before this timestamp"
    ),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> CasesListResponse:
    service = RecoveryOrchestratorService(db)
    return service.list_cases(
        limit=limit,
        offset=offset,
        status=status_filter,
        priority=priority,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@cases_router.get(
    "/{case_id}",
    response_model=RecoveryCaseDetail,
    summary="Get comprehensive recovery case detail with actions and timeline",
    operation_id="get_recovery_case_detail",
)
def get_case_detail(
    case_id: str,
    db: Session = Depends(get_db),
) -> RecoveryCaseDetail:
    service = RecoveryOrchestratorService(db)
    case_detail = service.get_case_detail(case_id)
    if not case_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recovery case with ID '{case_id}' was not found.",
        )
    return case_detail


# --- Promises Endpoints ---
@promises_router.get(
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


@promises_router.post(
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
