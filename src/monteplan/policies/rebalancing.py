"""Rebalancing policies: calendar and threshold-based."""

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


def rebalance_if_drifted(
    state: SimulationState,
    target_weights: np.ndarray,
    threshold: float,
) -> None:
    """Rebalance only paths where any asset drifted beyond threshold.

    For each path, compute the current portfolio-level weights. If any
    asset's weight deviates from target by more than ``threshold``,
    rebalance that path's accounts to targets. Paths within tolerance
    are left untouched.

    Args:
        state: Current simulation state (positions will be mutated).
        target_weights: (n_assets,) target allocation weights summing to 1.
        threshold: Maximum allowed absolute drift (e.g. 0.05 for 5%).
    """
    # Compute current portfolio-level weights: (n_paths, n_assets)
    total_per_asset = state.positions.sum(axis=1)  # (n_paths, n_assets)
    total_wealth = total_per_asset.sum(axis=1, keepdims=True)  # (n_paths, 1)
    safe_total = np.where(total_wealth > 0, total_wealth, 1.0)
    current_weights = total_per_asset / safe_total  # (n_paths, n_assets)

    # Check which paths have drifted beyond threshold
    drift = np.abs(current_weights - target_weights[np.newaxis, :])
    needs_rebalance = np.any(drift > threshold, axis=1)  # (n_paths,)

    if not needs_rebalance.any():
        return

    # Rebalance only drifted paths
    balances = state.balances  # (n_paths, n_accounts)
    new_positions = balances[:, :, np.newaxis] * target_weights[np.newaxis, np.newaxis, :]
    state.positions = np.where(
        needs_rebalance[:, np.newaxis, np.newaxis],
        new_positions,
        state.positions,
    )
