import logging

logger = logging.getLogger("app.analytics.roi")


class ROICalculator:
    """
    ROI, cost-benefit & net recovery calculations.
    """

    @staticmethod
    def calculate_net_recovery(total_recovered: float, total_cost: float) -> float:
        """Calculates net revenue recovered after factoring all operational & incentive costs."""
        return round(total_recovered - total_cost, 2)

    @staticmethod
    def calculate_roi_percentage(total_recovered: float, total_cost: float) -> float:
        """
        Calculates Return on Investment (ROI) percentage.
        ROI = ((Recovered - Cost) / Cost) * 100 if Cost > 0 else 0.0
        """
        if total_cost <= 0:
            return 0.0
        return round(((total_recovered - total_cost) / total_cost) * 100.0, 2)

    @staticmethod
    def calculate_cost_benefit_ratio(total_recovered: float, total_cost: float) -> float:
        """
        Calculates Cost-Benefit Ratio (₹ recovered per ₹1 spent).
        Ratio = Recovered / Cost if Cost > 0 else Recovered
        """
        if total_cost <= 0:
            return round(total_recovered, 2)
        return round(total_recovered / total_cost, 2)
