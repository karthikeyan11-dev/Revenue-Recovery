from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recovery_case import CaseStatus
from app.schemas.cases import CasesListResponse, RecoveryCaseDetail
from app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/cases", tags=["Recovery Cases"])


@router.get(
    "",
    response_model=CasesListResponse,
    summary="List recovery cases with filtering and pagination",
    operation_id="list_recovery_cases",
)
def list_cases(
    status_filter: CaseStatus | None = Query(
        None, alias="status", description="Filter by case status"
    ),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> CasesListResponse:
    service = RecoveryService(db)
    return service.list_cases(limit=limit, offset=offset, status=status_filter)


@router.get(
    "/{case_id}",
    response_model=RecoveryCaseDetail,
    summary="Get comprehensive recovery case detail with actions and timeline",
    operation_id="get_recovery_case_detail",
)
def get_case_detail(
    case_id: str,
    db: Session = Depends(get_db),
) -> RecoveryCaseDetail:
    service = RecoveryService(db)
    case_detail = service.get_case_detail(case_id)
    if not case_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recovery case with ID '{case_id}' was not found.",
        )
    return case_detail
