"""Tests for withdrawal ordering."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState
from monteplan.policies.withdrawals import withdraw


def _make_state(
    balances: list[list[float]],
    account_types: list[str],
) -> SimulationState:
    n_paths = len(balances)
    bal = np.array(balances, dtype=float)
    return SimulationState(
        balances=bal,
        cumulative_inflation=np.ones(n_paths),
        is_depleted=np.zeros(n_paths, dtype=bool),
        step=0,
        n_paths=n_paths,
        n_accounts=bal.shape[1],
        account_types=account_types,
    )


class TestWithdrawals:
    def test_taxable_first(self) -> None:
        """Should withdraw from taxable before traditional."""
        state = _make_state(
            [[50_000, 100_000, 30_000]],
            ["taxable", "traditional", "roth"],
        )
        need = np.array([10_000.0])
        got = withdraw(state, need, ["taxable", "traditional", "roth"], tax_rate=0.22)
        np.testing.assert_allclose(got, [10_000.0])
        # Should come entirely from taxable
        np.testing.assert_allclose(state.balances[0, 0], 40_000.0)
        np.testing.assert_allclose(state.balances[0, 1], 100_000.0)
        np.testing.assert_allclose(state.balances[0, 2], 30_000.0)

    def test_traditional_grossed_up(self) -> None:
        """Traditional withdrawals should be grossed up for taxes."""
        state = _make_state(
            [[0, 100_000, 0]],
            ["taxable", "traditional", "roth"],
        )
        need = np.array([7_800.0])  # after-tax need
        tax_rate = 0.22
        got = withdraw(state, need, ["taxable", "traditional", "roth"], tax_rate=tax_rate)
        np.testing.assert_allclose(got, [7_800.0])
        # Gross withdrawal = 7800 / (1 - 0.22) = 10000
        np.testing.assert_allclose(state.balances[0, 1], 90_000.0)

    def test_cascade_through_accounts(self) -> None:
        """When taxable is depleted, should cascade to traditional."""
        state = _make_state(
            [[5_000, 100_000, 50_000]],
            ["taxable", "traditional", "roth"],
        )
        need = np.array([8_000.0])
        got = withdraw(state, need, ["taxable", "traditional", "roth"], tax_rate=0.22)
        np.testing.assert_allclose(got, [8_000.0])
        # Taxable fully depleted
        np.testing.assert_allclose(state.balances[0, 0], 0.0)
        # Remaining 3000 after-tax from traditional = 3000 / 0.78 gross
        expected_trad = 100_000 - 3_000 / 0.78
        np.testing.assert_allclose(state.balances[0, 1], expected_trad, atol=0.01)

    def test_no_negative_balances(self) -> None:
        """Should never produce negative balances."""
        state = _make_state(
            [[1_000, 2_000, 500]],
            ["taxable", "traditional", "roth"],
        )
        need = np.array([100_000.0])  # way more than available
        got = withdraw(state, need, ["taxable", "traditional", "roth"], tax_rate=0.22)
        assert np.all(state.balances >= -1e-10)
        assert got[0] < 100_000.0  # couldn't fulfill full need

    def test_vectorized(self) -> None:
        """Should work correctly across multiple paths."""
        state = _make_state(
            [[50_000, 100_000], [10_000, 20_000]],
            ["taxable", "traditional"],
        )
        need = np.array([5_000.0, 5_000.0])
        got = withdraw(state, need, ["taxable", "traditional"], tax_rate=0.20)
        np.testing.assert_allclose(got, [5_000.0, 5_000.0])
