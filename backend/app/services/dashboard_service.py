import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardComparisonResponse, DashboardMetricsResponse
from app.services.metrics_calculator import UnifiedMetricsEngine

logger = logging.getLogger("app.services.dashboard")


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = UnifiedMetricsEngine(db)

    def get_dashboard_summary(
        self,
        time_range: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> DashboardMetricsResponse:
        return self.engine.get_dashboard_summary(
            time_range=time_range,
            date_from=date_from,
            date_to=date_to,
        )

    def get_dashboard_comparison(
        self,
        time_range: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> DashboardComparisonResponse:
        return self.engine.get_strategy_comparison(
            time_range=time_range,
            date_from=date_from,
            date_to=date_to,
        )


# Compatibility alias
AnalyticsService = DashboardService

