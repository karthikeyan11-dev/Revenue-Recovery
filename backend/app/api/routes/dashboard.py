from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardComparisonResponse, DashboardMetricsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardMetricsResponse,
    summary="Get executive dashboard recovery headline numbers and comparison chart",
    operation_id="get_dashboard_summary",
)
def get_dashboard_summary(
    time_range: str | None = Query(None, description="Time range filter (7d, 30d, 90d, all)"),
    date_from: datetime | None = Query(None, description="Start date filter"),
    date_to: datetime | None = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
) -> DashboardMetricsResponse:
    service = DashboardService(db)
    return service.get_dashboard_summary(
        time_range=time_range,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/comparison",
    response_model=DashboardComparisonResponse,
    summary="Get baseline vs AI recovery comparative performance and uplift analysis",
    operation_id="get_dashboard_comparison",
)
def get_dashboard_comparison(
    time_range: str | None = Query(None, description="Time range filter (7d, 30d, 90d, all)"),
    date_from: datetime | None = Query(None, description="Start date filter"),
    date_to: datetime | None = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
) -> DashboardComparisonResponse:
    service = DashboardService(db)
    return service.get_dashboard_comparison(
        time_range=time_range,
        date_from=date_from,
        date_to=date_to,
    )

