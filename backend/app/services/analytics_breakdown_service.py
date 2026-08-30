from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.analytics import AnalyticsBreakdownResponse
from app.services.metrics_calculator import UnifiedMetricsEngine


class AnalyticsBreakdownService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = UnifiedMetricsEngine(db)

    def get_breakdown(
        self,
        time_range: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AnalyticsBreakdownResponse:
        return self.engine.get_analytics_breakdown(
            time_range=time_range,
            date_from=date_from,
            date_to=date_to,
        )
