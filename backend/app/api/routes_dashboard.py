from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardMetricsResponse,
    summary="Get executive dashboard recovery headline numbers and comparison chart",
    operation_id="get_dashboard_summary",
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
) -> DashboardMetricsResponse:
    service = AnalyticsService(db)
    return service.get_dashboard_summary()
