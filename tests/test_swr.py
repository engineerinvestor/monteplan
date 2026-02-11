"""Tests for safe withdrawal rate finder."""

from __future__ import annotations

import pytest

from monteplan.analytics.swr import SWRResult, find_safe_withdrawal_rate
from monteplan.config.defaults import default_market, default_plan, default_policies
from monteplan.config.schema import SimulationConfig


class TestSWRFinder:
    """Tests for find_safe_withdrawal_rate."""

    def test_converges_and_meets_target(self) -> None:
        """Finder converges and achieves at least the target success rate."""
        result = find_safe_withdrawal_rate(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=500, seed=42),
            target_success_rate=0.90,
        )
        assert isinstance(result, SWRResult)
        assert result.achieved_success_rate >= result.target_success_rate
        assert result.max_monthly_spending >= 0
        assert result.iterations > 0

    def test_higher_target_lower_spending(self) -> None:
        """Higher target success rate → lower maximum spending (monotonicity)."""
        sim = SimulationConfig(n_paths=500, seed=42)
        plan = default_plan()
        market = default_market()
        policies = default_policies()

        result_90 = find_safe_withdrawal_rate(
            plan, market, policies, sim,
            target_success_rate=0.90,
        )
        result_95 = find_safe_withdrawal_rate(
            plan, market, policies, sim,
            target_success_rate=0.95,
        )
        assert result_95.max_monthly_spending <= result_90.max_monthly_spending

    def test_respects_max_iterations(self) -> None:
        """Finder respects max_iterations bound."""
        result = find_safe_withdrawal_rate(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            target_success_rate=0.90,
            max_iterations=5,
        )
        assert result.iterations <= 5

    def test_deterministic_with_fixed_seed(self) -> None:
        """Same seed produces same result."""
        sim = SimulationConfig(n_paths=500, seed=42)
        r1 = find_safe_withdrawal_rate(
            default_plan(), default_market(), default_policies(), sim,
            target_success_rate=0.90,
        )
        r2 = find_safe_withdrawal_rate(
            default_plan(), default_market(), default_policies(), sim,
            target_success_rate=0.90,
        )
        assert r1.max_monthly_spending == pytest.approx(r2.max_monthly_spending)

    def test_implied_rate_consistent(self) -> None:
        """Implied withdrawal rate = annual / initial_portfolio."""
        result = find_safe_withdrawal_rate(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            target_success_rate=0.90,
        )
        expected_rate = result.annual_withdrawal_amount / result.initial_portfolio
        assert result.implied_withdrawal_rate == pytest.approx(expected_rate)

    def test_initial_portfolio_matches_plan(self) -> None:
        """initial_portfolio should equal sum of account balances."""
        plan = default_plan()
        result = find_safe_withdrawal_rate(
            plan,
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            target_success_rate=0.90,
        )
        expected = sum(a.balance for a in plan.accounts)
        assert result.initial_portfolio == pytest.approx(expected)
