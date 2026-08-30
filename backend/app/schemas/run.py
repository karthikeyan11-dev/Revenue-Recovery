from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analyst import StrategyMetrics


class GenerateDataRequest(BaseModel):
    transaction_count: int = Field(
        default=500,
        ge=10,
        le=5000,
        description="Number of synthetic transactions to generate",
    )
    failure_rate: float = Field(
        default=0.25,
        ge=0.05,
        le=0.90,
        description="Simulated payment failure rate (e.g., 0.25 = 25%)",
    )
    clear_existing: bool = Field(
        default=True,
        description="Cleanly clear previous cohorts before seeding to prevent uncontrolled row accumulation",
    )


class GenerateDataResponse(BaseModel):
    status: str
    customers_generated: int
    transactions_generated: int
    failures_generated: int
    message: str


class SimulationStepTelemetry(BaseModel):
    name: str
    duration_formatted: str
    duration_seconds: float
    status: str = "Completed"
    summary: str


class RunStrategyRequest(BaseModel):
    simulation_name: str | None = Field(
        default=None,
        description="Custom name for this simulation run (e.g. 'High Value Focus')",
    )
    limit: int | None = Field(
        default=None,
        description="Optional limit on cases to process in this run",
    )
    use_mock_llm: bool = Field(
        default=False,
        description="Use fast deterministic mock LLM predictions for local demo runs if API key absent",
    )


class RunStrategyResponse(BaseModel):
    simulation_id: str | None = None
    simulation_name: str | None = None
    status: str
    strategy: str
    cases_processed: int
    metrics: StrategyMetrics
    step_telemetry: list[SimulationStepTelemetry] = []
    message: str


class SimulationHistoryItem(BaseModel):
    id: str
    name: str
    strategy_type: str
    status: str = "Completed"
    recovered_amount: float
    recovery_rate_percent: float
    total_revenue_at_risk: float
    cases_count: int
    step_telemetry: list[SimulationStepTelemetry] = []
    run_at: datetime


class SimulationHistoryResponse(BaseModel):
    simulations: list[SimulationHistoryItem]
    total: int
