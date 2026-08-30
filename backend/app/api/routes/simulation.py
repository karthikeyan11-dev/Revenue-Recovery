from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.generators.synthetic_generator import SyntheticDataGenerator
from app.schemas.run import (
    GenerateDataRequest,
    GenerateDataResponse,
    RunStrategyRequest,
    RunStrategyResponse,
    SimulationHistoryResponse,
    SimulationStepTelemetry,
)
from app.services.simulation_service import SimulationService

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
        clear_existing=payload.clear_existing,
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
    service = SimulationService(db)
    metrics = service.run_baseline_simulation(
        limit=payload.limit,
        simulation_name=payload.simulation_name,
    )
    steps = [SimulationStepTelemetry(**s) for s in (metrics.step_telemetry or [])]
    return RunStrategyResponse(
        simulation_id=metrics.simulation_id,
        simulation_name=metrics.simulation_name,
        status="completed",
        strategy="BASELINE_RETRY_ONCE",
        cases_processed=metrics.cases_count,
        metrics=metrics,
        step_telemetry=steps,
        message=f"Naive retry-once simulation '{metrics.simulation_name}' executed successfully.",
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
    service = SimulationService(db)
    metrics = service.run_ai_simulation(
        limit=payload.limit,
        use_mock=payload.use_mock_llm,
        simulation_name=payload.simulation_name,
    )
    steps = [SimulationStepTelemetry(**s) for s in (metrics.step_telemetry or [])]
    return RunStrategyResponse(
        simulation_id=metrics.simulation_id,
        simulation_name=metrics.simulation_name,
        status="completed",
        strategy="AI_ORCHESTRATOR",
        cases_processed=metrics.cases_count,
        metrics=metrics,
        step_telemetry=steps,
        message=f"AI multi-agent recovery orchestrator simulation '{metrics.simulation_name}' executed successfully.",
    )


@router.get(
    "/simulations/history",
    response_model=SimulationHistoryResponse,
    summary="Get recent persisted simulation runs and step execution telemetry",
    operation_id="get_simulation_history",
)
def get_simulation_history(
    limit: int = Query(10, ge=1, le=50, description="Max simulation history records to fetch"),
    db: Session = Depends(get_db),
) -> SimulationHistoryResponse:
    service = SimulationService(db)
    return service.get_simulation_history(limit=limit)
