"""Tests for simulation metrics."""

from __future__ import annotations

import numpy as np

from monteplan.analytics.metrics import compute_metrics


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
