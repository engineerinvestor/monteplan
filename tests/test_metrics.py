"""Tests for simulation metrics."""

from __future__ import annotations

import numpy as np

from monteplan.analytics.metrics import (
    compute_metrics,
    max_drawdown_distribution,
    ruin_by_age,
    spending_volatility,
)


class TestMetrics:
    def test_all_success(self) -> None:
        """All paths survive → 100% success."""
        wealth = np.ones((10, 100)) * 1000
        m = compute_metrics(wealth, retirement_step=50)
        assert m.success_probability == 1.0
        assert m.shortfall_probability == 0.0
        assert m.mean_shortfall == 0.0

    def test_all_failure(self) -> None:
        """All paths hit zero in retirement → 0% success."""
        wealth = np.ones((10, 100)) * 1000
        wealth[:, 60:] = 0  # zero from step 60 onward
        m = compute_metrics(wealth, retirement_step=50)
        assert m.success_probability == 0.0
        assert m.shortfall_probability == 1.0
        assert m.mean_shortfall > 0

    def test_partial_success(self) -> None:
        """Half succeed, half fail."""
        wealth = np.ones((10, 100)) * 1000
        wealth[5:, 70:] = 0  # bottom half depletes
        m = compute_metrics(wealth, retirement_step=50)
        assert m.success_probability == 0.5

    def test_terminal_percentiles_ordered(self) -> None:
        rng = np.random.default_rng(42)
        wealth = np.cumsum(rng.normal(100, 50, (1000, 100)), axis=1)
        wealth = np.maximum(wealth, 0)
        m = compute_metrics(wealth, retirement_step=50)
        assert m.terminal_wealth_p5 <= m.terminal_wealth_p25
        assert m.terminal_wealth_p25 <= m.terminal_wealth_p50
        assert m.terminal_wealth_p50 <= m.terminal_wealth_p75
        assert m.terminal_wealth_p75 <= m.terminal_wealth_p95


class TestMaxDrawdown:
    def test_no_drawdown(self) -> None:
        """Monotonically increasing wealth → zero drawdown."""
        wealth = np.arange(1, 101, dtype=float).reshape(1, -1)
        dd = max_drawdown_distribution(wealth)
        assert dd["p50"] == 0.0

    def test_complete_drawdown(self) -> None:
        """Wealth goes to zero → 100% drawdown."""
        wealth = np.array([[1000, 500, 0]])
        dd = max_drawdown_distribution(wealth)
        assert dd["p50"] == 1.0

    def test_partial_drawdown(self) -> None:
        """50% drawdown from peak."""
        wealth = np.array([[1000, 500, 750]])
        dd = max_drawdown_distribution(wealth)
        np.testing.assert_allclose(dd["p50"], 0.5, atol=1e-10)

    def test_percentiles_ordered(self) -> None:
        rng = np.random.default_rng(42)
        wealth = np.cumsum(rng.normal(100, 50, (500, 200)), axis=1)
        wealth = np.maximum(wealth, 1)
        dd = max_drawdown_distribution(wealth)
        assert dd["p5"] <= dd["p25"] <= dd["p50"] <= dd["p75"] <= dd["p95"]


class TestSpendingVolatility:
    def test_constant_spending(self) -> None:
        """Constant spending → zero volatility."""
        spending = np.full((10, 100), 3000.0)
        sv = spending_volatility(spending, retirement_step=50)
        assert sv["p50"] == 0.0
        assert sv["mean"] == 0.0

    def test_variable_spending(self) -> None:
        """Variable spending → non-zero volatility."""
        rng = np.random.default_rng(42)
        spending = 3000 + rng.normal(0, 100, (100, 200))
        spending = np.maximum(spending, 0)
        sv = spending_volatility(spending, retirement_step=50)
        assert sv["mean"] > 0

    def test_short_retirement(self) -> None:
        """Less than 2 retirement steps → zero volatility."""
        spending = np.array([[3000.0]])
        sv = spending_volatility(spending, retirement_step=0)
        assert sv["p50"] == 0.0


class TestRuinByAge:
    def test_no_ruin(self) -> None:
        """All paths survive → zero ruin everywhere."""
        wealth = np.ones((10, 100)) * 1000
        ages, fracs = ruin_by_age(wealth, retirement_step=50, current_age=60)
        assert fracs.max() == 0.0
        assert len(ages) == 50

    def test_all_ruin(self) -> None:
        """All paths zero immediately → 100% ruin."""
        wealth = np.ones((10, 100)) * 1000
        wealth[:, 50:] = 0
        ages, fracs = ruin_by_age(wealth, retirement_step=50, current_age=60)
        assert fracs[-1] == 1.0

    def test_ages_monotonic(self) -> None:
        """Ages should be monotonically increasing."""
        wealth = np.ones((10, 100)) * 1000
        ages, fracs = ruin_by_age(wealth, retirement_step=50, current_age=30)
        assert np.all(np.diff(ages) >= 0)
