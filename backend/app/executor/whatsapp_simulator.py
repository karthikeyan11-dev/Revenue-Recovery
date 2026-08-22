import random

from app.models.communication_event import SimulatedResponse


class WhatsAppSimulator:
    """
    Simulates interactive WhatsApp recovery messages, link clicks, and payments.
    """

    @staticmethod
    def simulate_interaction(has_discount: bool = False) -> tuple[SimulatedResponse, str]:
        # WhatsApp has high open rate (80%+)
        roll = random.random()

        if has_discount:
            # Higher conversion when discount incentive is provided
            if roll < 0.65:
                return (
                    SimulatedResponse.PAID,
                    "Customer opened WhatsApp, applied coupon, and paid successfully",
                )
            if roll < 0.85:
                return SimulatedResponse.CLICKED, "Customer opened message and clicked payment link"
            if roll < 0.95:
                return SimulatedResponse.OPENED, "Customer read message but did not click"
            return SimulatedResponse.IGNORED, "Message delivered but ignored"

        # Standard recovery message
        if roll < 0.45:
            return SimulatedResponse.PAID, "Customer opened WhatsApp and completed payment"
        if roll < 0.70:
            return SimulatedResponse.CLICKED, "Customer clicked link but abandoned checkout"
        if roll < 0.90:
            return SimulatedResponse.OPENED, "Customer read message"
        return SimulatedResponse.IGNORED, "Message delivered but ignored"
