"""Tests for spending policies."""

from __future__ import annotations

import numpy as np

from monteplan.core.state import SimulationState
from monteplan.policies.spending.constant_real import ConstantRealSpending
from monteplan.policies.spending.percent_of_portfolio import PercentOfPortfolioSpending


def _make_state(
    balances: list[list[float]],
    cumulative_inflation: list[float] | None = None,
) -> SimulationState:
    n_paths = len(balances)
    bal = np.array(balances)
    if cumulative_inflation is None:
        cumulative_inflation = [1.0] * n_paths
    return SimulationState(
        balances=bal,
        cumulative_inflation=np.array(cumulative_inflation),
        is_depleted=np.zeros(n_paths, dtype=bool),
        step=0,
        n_paths=n_paths,
        n_accounts=bal.shape[1],
        account_types=["taxable"] * bal.shape[1],
    )


class TestConstantReal:
    def test_no_inflation(self) -> None:
        policy = ConstantRealSpending(5000.0)
        state = _make_state([[100_000]], [1.0])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [5000.0])

    def test_with_inflation(self) -> None:
        policy = ConstantRealSpending(5000.0)
        state = _make_state([[100_000]], [1.1])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [5500.0])

    def test_vectorized(self) -> None:
        policy = ConstantRealSpending(1000.0)
        state = _make_state([[50_000], [80_000]], [1.0, 1.5])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [1000.0, 1500.0])


class TestPercentOfPortfolio:
    def test_basic(self) -> None:
        policy = PercentOfPortfolioSpending(0.04)  # 4% annual
        state = _make_state([[1_000_000]])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [1_000_000 * 0.04 / 12])

    def test_zero_wealth(self) -> None:
        policy = PercentOfPortfolioSpending(0.04)
        state = _make_state([[0.0]])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [0.0])

    def test_multiple_accounts(self) -> None:
        policy = PercentOfPortfolioSpending(0.04)
        state = _make_state([[500_000, 500_000]])
        result = policy.compute(state)
        np.testing.assert_allclose(result, [1_000_000 * 0.04 / 12])
