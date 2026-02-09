"""Tests for rebalancing policy (v0.1 no-op hook)."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState
from monteplan.policies.rebalancing import rebalance_to_targets


class TestRebalancing:
    def test_no_op_preserves_balances(self) -> None:
        """v0.1 rebalancing is a no-op; balances should be unchanged."""
        balances = np.array([[100_000.0, 50_000.0]])
        state = SimulationState(
            balances=balances.copy(),
            cumulative_inflation=np.ones(1),
            is_depleted=np.zeros(1, dtype=bool),
            step=0,
            n_paths=1,
            n_accounts=2,
            account_types=["taxable", "traditional"],
        )
        target_weights = np.array([0.7, 0.3])
        rebalance_to_targets(state, target_weights)
        np.testing.assert_array_equal(state.balances, balances)
