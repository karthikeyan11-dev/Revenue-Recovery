import random

from app.models.communication_event import SimulatedResponse


class EmailSimulator:
    """
    Simulates email dunning notifications, open rates, and click-to-pay.
    """

    @staticmethod
    def simulate_interaction(has_discount: bool = False) -> tuple[SimulatedResponse, str]:
        roll = random.random()

        if has_discount:
            if roll < 0.45:
                return (
                    SimulatedResponse.PAID,
                    "Customer opened dunning email, applied discount, and completed payment",
                )
            if roll < 0.70:
                return SimulatedResponse.CLICKED, "Customer clicked payment button from email"
            if roll < 0.88:
                return SimulatedResponse.OPENED, "Customer opened email"
            return SimulatedResponse.IGNORED, "Email delivered to inbox/promotions but not opened"

        if roll < 0.32:
            return SimulatedResponse.PAID, "Customer paid through email recovery link"
        if roll < 0.55:
            return SimulatedResponse.CLICKED, "Customer clicked recovery link"
        if roll < 0.80:
            return SimulatedResponse.OPENED, "Customer opened email"
        return SimulatedResponse.IGNORED, "Email ignored"
