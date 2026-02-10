"""Simulation result metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SimulationMetrics:
    """Computed metrics from a simulation run."""

    success_probability: float
    terminal_wealth_p5: float
    terminal_wealth_p25: float
    terminal_wealth_p50: float
    terminal_wealth_p75: float
    terminal_wealth_p95: float
    mean_terminal_wealth: float
    mean_shortfall: float
    shortfall_probability: float


def compute_metrics(
    wealth_history: np.ndarray,
    retirement_step: int,
) -> SimulationMetrics:
    """Compute simulation metrics from wealth history.

    Args:
        wealth_history: (n_paths, n_steps+1) array of total wealth at each step.
        retirement_step: Step index when retirement begins.

    Returns:
        SimulationMetrics with success/failure statistics.
    """
    retirement_wealth = wealth_history[:, retirement_step:]

    # Success = never ran out during retirement
    success_mask = np.all(retirement_wealth > 0, axis=1)
    success_probability = float(success_mask.mean())

    # Terminal wealth
    terminal = wealth_history[:, -1]
    pcts = np.percentile(terminal, [5, 25, 50, 75, 95])

    # Shortfall: paths where terminal wealth is 0
    failed_mask = ~success_mask
    shortfall_probability = float(failed_mask.mean())

    if failed_mask.any():
        # Mean number of months with zero wealth across failed paths
        zero_months = (retirement_wealth[failed_mask] <= 0).sum(axis=1)
        mean_shortfall = float(zero_months.mean())
    else:
        mean_shortfall = 0.0

    return SimulationMetrics(
        success_probability=success_probability,
        terminal_wealth_p5=float(pcts[0]),
        terminal_wealth_p25=float(pcts[1]),
        terminal_wealth_p50=float(pcts[2]),
        terminal_wealth_p75=float(pcts[3]),
        terminal_wealth_p95=float(pcts[4]),
        mean_terminal_wealth=float(terminal.mean()),
        mean_shortfall=mean_shortfall,
        shortfall_probability=shortfall_probability,
    )


def max_drawdown_distribution(
    wealth_history: np.ndarray,
) -> dict[str, float]:
    """Compute per-path maximum drawdown and return percentiles.

    Maximum drawdown = largest peak-to-trough decline as a fraction.

    Args:
        wealth_history: (n_paths, n_steps+1) array of total wealth.

    Returns:
        Dict with p5, p25, p50, p75, p95, mean of max drawdown (as fractions).
    """
    # Running maximum along the time axis
    running_max = np.maximum.accumulate(wealth_history, axis=1)
    safe_max = np.where(running_max > 0, running_max, 1.0)
    drawdowns = (running_max - wealth_history) / safe_max
    # Per-path max drawdown
    max_dd = drawdowns.max(axis=1)

    pcts = np.percentile(max_dd, [5, 25, 50, 75, 95])
    return {
        "p5": float(pcts[0]),
        "p25": float(pcts[1]),
        "p50": float(pcts[2]),
        "p75": float(pcts[3]),
        "p95": float(pcts[4]),
        "mean": float(max_dd.mean()),
    }


def spending_volatility(
    spending_history: np.ndarray,
    retirement_step: int,
) -> dict[str, float]:
    """Compute per-path spending volatility during retirement.

    Volatility = standard deviation of month-over-month spending changes
    divided by mean spending (coefficient of variation of changes).

    Args:
        spending_history: (n_paths, n_steps) array of monthly spending.
        retirement_step: Step index when retirement begins.

    Returns:
        Dict with p50 and mean of spending volatility across paths.
    """
    retirement_spending = spending_history[:, retirement_step:]

    # Month-over-month changes
    if retirement_spending.shape[1] < 2:
        return {"p50": 0.0, "mean": 0.0}

    changes = np.diff(retirement_spending, axis=1)
    mean_spending = retirement_spending[:, :-1].mean(axis=1)
    safe_mean = np.where(mean_spending > 0, mean_spending, 1.0)

    # Per-path coefficient of variation of changes
    change_std = changes.std(axis=1)
    cv = change_std / safe_mean

    return {
        "p50": float(np.median(cv)),
        "mean": float(cv.mean()),
    }


def ruin_by_age(
    wealth_history: np.ndarray,
    retirement_step: int,
    current_age: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute fraction of paths depleted at each age.

    Args:
        wealth_history: (n_paths, n_steps+1) array of total wealth.
        retirement_step: Step index when retirement begins.
        current_age: Starting age.

    Returns:
        Tuple of (ages, ruin_fractions) arrays.
    """
    n_paths, n_time = wealth_history.shape
    # Check depletion at each step from retirement onward
    retired_wealth = wealth_history[:, retirement_step:]
    depleted = retired_wealth <= 0  # (n_paths, n_retirement_steps)
    # Cumulative: once depleted, stays depleted
    cumulative_depleted = np.maximum.accumulate(depleted.astype(int), axis=1)
    ruin_fractions = cumulative_depleted.mean(axis=0)

    # Ages for each step
    n_retirement_steps = retired_wealth.shape[1]
    ages = np.linspace(
        current_age + retirement_step / 12.0,
        current_age + (retirement_step + n_retirement_steps - 1) / 12.0,
        n_retirement_steps,
    )
    return ages, ruin_fractions
