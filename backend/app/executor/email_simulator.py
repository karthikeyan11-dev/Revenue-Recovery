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
            if roll < 0.40:
                return (
                    SimulatedResponse.PAID,
                    "Customer opened dunning email, applied discount, and completed payment",
                )
            if roll < 0.65:
                return SimulatedResponse.CLICKED, "Customer clicked payment button from email"
            if roll < 0.85:
                return SimulatedResponse.OPENED, "Customer opened email"
            return SimulatedResponse.IGNORED, "Email delivered to inbox/promotions but not opened"

        if roll < 0.28:
            return SimulatedResponse.PAID, "Customer paid through email recovery link"
        if roll < 0.50:
            return SimulatedResponse.CLICKED, "Customer clicked recovery link"
        if roll < 0.75:
            return SimulatedResponse.OPENED, "Customer opened email"
        return SimulatedResponse.IGNORED, "Email ignored"
