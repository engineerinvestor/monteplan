"""Calendar rebalancing policy."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState


def rebalance_to_targets(
    state: SimulationState,
    target_weights: np.ndarray,
) -> None:
    """Rebalance all accounts to target allocation weights.

    In v0.1, each account holds the full portfolio blend (not per-asset).
    Rebalancing redistributes total wealth across accounts proportional to
    their current share of total wealth, maintaining the same total.

    This is effectively a no-op for portfolio returns since we apply a
    blended return. The real rebalancing (drift-aware, per-asset-per-account)
    comes in v0.2. Keeping the function as a hook point.

    Args:
        state: Current simulation state.
        target_weights: Target asset weights (not used in v0.1 — implicit).
    """
    # In v0.1, rebalancing is implicit: we always apply portfolio-weighted
    # blended returns, so accounts are always "at target." This function
    # exists as a hook for v0.2.
    pass
