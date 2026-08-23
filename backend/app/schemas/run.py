from pydantic import BaseModel, Field

from app.schemas.analyst import StrategyMetrics


class GenerateDataRequest(BaseModel):
    transaction_count: int = Field(
        default=500,
        ge=50,
        le=5000,
        description="Number of synthetic transactions to generate",
    )
    failure_rate: float = Field(
        default=0.25,
        ge=0.05,
        le=0.90,
        description="Simulated payment failure rate (e.g., 0.25 = 25%)",
    )


class GenerateDataResponse(BaseModel):
    status: str
    customers_generated: int
    transactions_generated: int
    failures_generated: int
    message: str


class RunStrategyRequest(BaseModel):
    limit: int | None = Field(
        default=None,
        description="Optional limit on cases to process in this run",
    )
    use_mock_llm: bool = Field(
        default=False,
        description="Use fast deterministic mock LLM predictions for local demo runs if API key absent",
    )


class RunStrategyResponse(BaseModel):
    status: str
    strategy: str
    cases_processed: int
    metrics: StrategyMetrics
    message: str
