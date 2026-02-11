"""Tests for top-level package exports."""

from __future__ import annotations

import monteplan


class TestExports:
    """All public exports should be importable from the top-level package."""

    def test_version(self) -> None:
        assert monteplan.__version__ == "0.5.0"

    def test_simulate(self) -> None:
        assert callable(monteplan.simulate)

    def test_simulation_result(self) -> None:
        assert monteplan.SimulationResult is not None

    def test_plan_config(self) -> None:
        assert monteplan.PlanConfig is not None

    def test_market_assumptions(self) -> None:
        assert monteplan.MarketAssumptions is not None

    def test_policy_bundle(self) -> None:
        assert monteplan.PolicyBundle is not None

    def test_simulation_config(self) -> None:
        assert monteplan.SimulationConfig is not None

    def test_account_config(self) -> None:
        assert monteplan.AccountConfig is not None

    def test_asset_class(self) -> None:
        assert monteplan.AssetClass is not None

    def test_spending_policy_config(self) -> None:
        assert monteplan.SpendingPolicyConfig is not None

    def test_roth_conversion_config(self) -> None:
        assert monteplan.RothConversionConfig is not None

    def test_discrete_event(self) -> None:
        assert monteplan.DiscreteEvent is not None

    def test_glide_path(self) -> None:
        assert monteplan.GlidePath is not None

    def test_guaranteed_income_stream(self) -> None:
        assert monteplan.GuaranteedIncomeStream is not None

    def test_default_plan(self) -> None:
        plan = monteplan.default_plan()
        assert plan is not None

    def test_default_market(self) -> None:
        market = monteplan.default_market()
        assert market is not None

    def test_default_policies(self) -> None:
        policies = monteplan.default_policies()
        assert policies is not None

    def test_default_sim_config(self) -> None:
        sim = monteplan.default_sim_config()
        assert sim is not None

    def test_find_safe_withdrawal_rate(self) -> None:
        assert callable(monteplan.find_safe_withdrawal_rate)

    def test_swr_result(self) -> None:
        assert monteplan.SWRResult is not None
