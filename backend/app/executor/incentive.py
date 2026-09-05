import random
import string


class IncentiveService:
    @staticmethod
    def generate_coupon(discount_percent: float) -> str:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"RECOVER{int(discount_percent)}-{suffix}"

    @staticmethod
    def calculate_cost(amount: float, discount_percent: float) -> float:
        return (amount * discount_percent) / 100.0
