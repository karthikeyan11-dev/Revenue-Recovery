def calculate_laplace_confidence(
    successes: int,
    total_trials: int,
    alpha: float = 1.0,
    beta: float = 1.0,
) -> float:
    """
    Computes Laplace-smoothed empirical confidence score:
    P = (successes + alpha) / (total_trials + alpha + beta)
    Defaults to Uniform Beta Prior (alpha=1, beta=1) -> unobserved starts at 0.50.
    """
    return (successes + alpha) / (total_trials + alpha + beta)


def format_currency_inr(amount: float) -> str:
    """Formats float into INR currency string."""
    return f"₹{amount:,.2f}"
