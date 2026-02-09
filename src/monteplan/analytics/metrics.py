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
