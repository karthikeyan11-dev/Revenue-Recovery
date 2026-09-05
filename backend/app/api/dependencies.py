from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.services.promise_service import PromiseTrackerService
from app.services.recovery_orchestrator import RecoveryOrchestratorService
from app.services.simulation_service import SimulationService


def get_recovery_service(db: Session = Depends(get_db)) -> RecoveryOrchestratorService:
    return RecoveryOrchestratorService(db)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


def get_simulation_service(db: Session = Depends(get_db)) -> SimulationService:
    return SimulationService(db)


def get_promise_service(db: Session = Depends(get_db)) -> PromiseTrackerService:
    return PromiseTrackerService(db)
