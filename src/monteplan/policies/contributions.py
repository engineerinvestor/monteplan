"""Contribution policy: fixed monthly contributions during accumulation."""

from __future__ import annotations

from monteplan.core.state import SimulationState


def apply_contributions(
    state: SimulationState,
    monthly_contributions: list[float],
) -> None:
    """Add fixed monthly contributions to each account.

    Args:
        state: Current simulation state (balances will be mutated).
        monthly_contributions: Monthly contribution for each account.
    """
    for i, contrib in enumerate(monthly_contributions):
        if contrib > 0:
            state.balances[:, i] += contrib


def compute_monthly_contributions(annual_contributions: list[float]) -> list[float]:
    """Convert annual contributions to monthly amounts."""
    return [c / 12.0 for c in annual_contributions]
