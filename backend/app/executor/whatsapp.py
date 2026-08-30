import random

from app.models.communication_event import SimulatedResponse


class WhatsAppSimulator:
    """
    Simulates interactive WhatsApp recovery messages, link clicks, and payments.
    """

    @staticmethod
    def simulate_interaction(has_discount: bool = False) -> tuple[SimulatedResponse, str]:
        # WhatsApp has high open rate in India (80%+) with 1-click UPI deep links
        roll = random.random()

        if has_discount:
            # Higher conversion when discount incentive is provided (72%)
            if roll < 0.72:
                return (
                    SimulatedResponse.PAID,
                    "Customer opened WhatsApp, applied coupon, and paid via Razorpay UPI intent",
                )
            if roll < 0.88:
                return SimulatedResponse.CLICKED, "Customer opened message and clicked payment link"
            if roll < 0.96:
                return SimulatedResponse.OPENED, "Customer read message but did not click"
            return SimulatedResponse.IGNORED, "Message delivered but ignored"

        # Standard recovery message (55% UPI conversion)
        if roll < 0.55:
            return SimulatedResponse.PAID, "Customer opened WhatsApp and completed Razorpay UPI payment"
        if roll < 0.78:
            return SimulatedResponse.CLICKED, "Customer clicked link but abandoned checkout"
        if roll < 0.92:
            return SimulatedResponse.OPENED, "Customer read message"
        return SimulatedResponse.IGNORED, "Message delivered but ignored"
