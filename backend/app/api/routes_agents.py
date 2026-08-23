from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.recovery_repository import RecoveryRepository
from app.schemas.agents import AgentActivityFeedResponse, AgentActivityItem

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get(
    "/activity",
    response_model=AgentActivityFeedResponse,
    summary="Get recent agent reasoning activities and decision stream",
    operation_id="get_agent_activity_feed",
)
def get_agent_activity(
    limit: int = Query(50, ge=1, le=200, description="Max activities to fetch"),
    db: Session = Depends(get_db),
) -> AgentActivityFeedResponse:
    repo = RecoveryRepository(db)
    activities = repo.get_recent_activities(limit=limit)

    items = [
        AgentActivityItem(
            id=act.id,
            case_id=act.case_id,
            agent=act.agent,
            step_name=act.step_name,
            input_summary=act.input_summary,
            output_summary=act.output_summary,
            decision=act.decision,
            confidence=act.confidence,
            empirical_confidence=(
                act.empirical_confidence if act.empirical_confidence is not None else act.confidence
            ),
            llm_stated_confidence=act.llm_stated_confidence,
            precedent_sample_size=act.precedent_sample_size or 0,
            timestamp=act.timestamp,
        )
        for act in activities
    ]

    return AgentActivityFeedResponse(
        activities=items,
        total_events=len(items),
    )
