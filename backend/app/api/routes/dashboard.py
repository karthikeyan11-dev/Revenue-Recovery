from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.dashboard_service import DashboardService

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
    service = DashboardService(db)
    return service.get_dashboard_summary()
