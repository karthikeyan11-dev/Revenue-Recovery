from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.data.synthetic_generator import SyntheticDataGenerator
from app.db import get_db
from app.schemas.run import (
    GenerateDataRequest,
    GenerateDataResponse,
    RunStrategyRequest,
    RunStrategyResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Simulation Runs"])


@router.post(
    "/data/generate",
    response_model=GenerateDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate synthetic cohort transactions and payment failure records",
    operation_id="generate_synthetic_data",
)
def generate_data(
    payload: GenerateDataRequest,
    db: Session = Depends(get_db),
) -> GenerateDataResponse:
    customer_count = max(20, payload.transaction_count // 4)
    result = SyntheticDataGenerator.populate_database(
        db=db,
        customer_count=customer_count,
        transaction_count=payload.transaction_count,
        failure_rate=payload.failure_rate,
    )
    return GenerateDataResponse(**result)


@router.post(
    "/run/baseline",
    response_model=RunStrategyResponse,
    summary="Run naive retry-once benchmark strategy against current failures",
    operation_id="run_baseline_simulation",
)
def run_baseline(
    payload: RunStrategyRequest,
    db: Session = Depends(get_db),
) -> RunStrategyResponse:
    service = AnalyticsService(db)
    metrics = service.run_baseline_simulation(limit=payload.limit)
    return RunStrategyResponse(
        status="completed",
        strategy="BASELINE_RETRY_ONCE",
        cases_processed=metrics.cases_count,
        metrics=metrics,
        message="Naive retry-once simulation executed successfully.",
    )


@router.post(
    "/run/ai",
    response_model=RunStrategyResponse,
    summary="Run autonomous policy-governed multi-agent recovery workflow",
    operation_id="run_ai_orchestrator_simulation",
)
def run_ai(
    payload: RunStrategyRequest,
    db: Session = Depends(get_db),
) -> RunStrategyResponse:
    service = AnalyticsService(db)
    metrics = service.run_ai_simulation(limit=payload.limit, use_mock=payload.use_mock_llm)
    return RunStrategyResponse(
        status="completed",
        strategy="AI_ORCHESTRATOR",
        cases_processed=metrics.cases_count,
        metrics=metrics,
        message="AI multi-agent recovery orchestrator simulation executed successfully.",
    )
