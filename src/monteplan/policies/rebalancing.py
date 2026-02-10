"""Calendar rebalancing policy."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState


def rebalance_to_targets(
    state: SimulationState,
    target_weights: np.ndarray,
) -> None:
    """Rebalance all accounts to target allocation weights.

    For each account, redistributes positions across assets so that
    the dollar allocation matches ``target_weights`` while preserving
    the total account balance. Vectorized across all paths.

    Args:
        state: Current simulation state (positions will be mutated).
        target_weights: (n_assets,) target allocation weights summing to 1.
    """
    # balances shape: (n_paths, n_accounts)
    balances = state.balances
    # target positions: balances[:, :, np.newaxis] * target_weights
    # → (n_paths, n_accounts, n_assets)
    state.positions = balances[:, :, np.newaxis] * target_weights[np.newaxis, np.newaxis, :]
