import logging

from app.executor.email_simulator import EmailSimulator
from app.executor.incentive_service import IncentiveService
from app.executor.payment_simulator import PaymentSimulator
from app.executor.whatsapp_simulator import WhatsAppSimulator
from app.models.communication_event import CommunicationChannel, SimulatedResponse
from app.models.payment_failure import FailureReason
from app.models.recovery_action import ActionOutcome, ActionType, PolicyDecision

logger = logging.getLogger("app.executor")


class ExecutionResult:
    def __init__(
        self,
        outcome: ActionOutcome,
        recovered: bool,
        recovered_amount: float = 0.0,
        cost: float = 0.0,
        details: str = "",
        communication_event_data: dict | None = None,
    ):
        self.outcome = outcome
        self.recovered = recovered
        self.recovered_amount = recovered_amount
        self.cost = cost
        self.details = details
        self.communication_event_data = communication_event_data


class ActionExecutor:
    """
    Action Execution Dispatcher.
    Executes ONLY actions that have passed the deterministic policy engine.
    """

    @classmethod
    def execute(
        cls,
        action_type: ActionType,
        policy_decision: PolicyDecision,
        amount: float,
        failure_reason: FailureReason,
        attempt_number: int = 1,
        incentive_percent: float = 0.0,
        retry_delay_hours: int = 0,
        channel: str | None = None,
        customer_contact: str = "customer@example.com",
    ) -> ExecutionResult:
        if policy_decision == PolicyDecision.REJECTED:
            return ExecutionResult(
                outcome=ActionOutcome.BLOCKED,
                recovered=False,
                details="Action was blocked by policy engine. No execution dispatched.",
            )

        if (
            policy_decision == PolicyDecision.ESCALATED
            or action_type == ActionType.ESCALATE_TO_HUMAN
        ):
            return ExecutionResult(
                outcome=ActionOutcome.ESCALATED_WAITING,
                recovered=False,
                details="Action routed to Human Escalation Queue for manual review.",
            )

        if action_type == ActionType.WAIT:
            return ExecutionResult(
                outcome=ActionOutcome.PENDING,
                recovered=False,
                details=f"Strategy scheduled cooldown wait of {retry_delay_hours} hours.",
            )

        # 1. Smart Payment Retry Dispatch
        if action_type == ActionType.RETRY:
            success, message = PaymentSimulator.simulate_retry(
                failure_reason=failure_reason,
                attempt_number=attempt_number,
                delay_hours=retry_delay_hours,
            )
            return ExecutionResult(
                outcome=ActionOutcome.SUCCESS if success else ActionOutcome.FAILED,
                recovered=success,
                recovered_amount=amount if success else 0.0,
                cost=0.50,  # Estimated gateway retry API fee
                details=message,
            )

        # 2. WhatsApp Interactive Outreach
        if action_type == ActionType.SEND_WHATSAPP or (
            action_type == ActionType.OFFER_INCENTIVE and channel == "WHATSAPP"
        ):
            has_discount = incentive_percent > 0
            coupon = IncentiveService.generate_coupon(incentive_percent) if has_discount else None
            incentive_cost = (
                IncentiveService.calculate_cost(amount, incentive_percent) if has_discount else 0.0
            )

            response_status, message = WhatsAppSimulator.simulate_interaction(
                has_discount=has_discount
            )
            recovered = response_status == SimulatedResponse.PAID

            msg_content = f"Hi! We noticed your transaction of ₹{amount:,.2f} didn't go through."
            if coupon:
                msg_content += f" Use code {coupon} for {incentive_percent:.0f}% off to retry now: https://rzp.io/l/recov"

            return ExecutionResult(
                outcome=ActionOutcome.SUCCESS if recovered else ActionOutcome.FAILED,
                recovered=recovered,
                recovered_amount=amount if recovered else 0.0,
                cost=(incentive_cost if recovered else 0.0) + 1.20,  # WhatsApp message cost ₹1.20
                details=message,
                communication_event_data={
                    "channel": CommunicationChannel.WHATSAPP,
                    "recipient": customer_contact,
                    "message_content": msg_content,
                    "simulated_response": response_status,
                },
            )

        # 3. Email Dunning Outreach
        if (
            action_type == ActionType.SEND_EMAIL
            or action_type == ActionType.SEND_PAYMENT_LINK
            or (action_type == ActionType.OFFER_INCENTIVE and channel == "EMAIL")
        ):
            has_discount = incentive_percent > 0
            coupon = IncentiveService.generate_coupon(incentive_percent) if has_discount else None
            incentive_cost = (
                IncentiveService.calculate_cost(amount, incentive_percent) if has_discount else 0.0
            )

            response_status, message = EmailSimulator.simulate_interaction(
                has_discount=has_discount
            )
            recovered = response_status == SimulatedResponse.PAID

            msg_content = f"Payment update for Order: ₹{amount:,.2f}."
            if coupon:
                msg_content += f" Apply code {coupon} ({incentive_percent:.0f}% discount)."

            return ExecutionResult(
                outcome=ActionOutcome.SUCCESS if recovered else ActionOutcome.FAILED,
                recovered=recovered,
                recovered_amount=amount if recovered else 0.0,
                cost=(incentive_cost if recovered else 0.0) + 0.10,  # Email cost ₹0.10
                details=message,
                communication_event_data={
                    "channel": CommunicationChannel.EMAIL,
                    "recipient": customer_contact,
                    "message_content": msg_content,
                    "simulated_response": response_status,
                },
            )

        # Default fallback
        return ExecutionResult(
            outcome=ActionOutcome.FAILED,
            recovered=False,
            details="Unrecognized action type dispatched.",
        )
