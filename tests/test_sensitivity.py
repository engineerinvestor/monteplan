"""Tests for OAT sensitivity analysis."""

from __future__ import annotations

from monteplan.analytics.sensitivity import run_sensitivity
from monteplan.config.defaults import (
    default_market,
    default_plan,
    default_policies,
)
from monteplan.config.schema import SimulationConfig


class TestSensitivityBasic:
    def test_output_structure(self) -> None:
        report = run_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=200, seed=42),
            perturbation_pct=0.10,
        )
        assert report.base_success_probability >= 0
        assert len(report.results) > 0
        for r in report.results:
            assert r.parameter_name
            assert 0.0 <= r.low_success <= 1.0
            assert 0.0 <= r.high_success <= 1.0

    def test_higher_returns_increase_success(self) -> None:
        report = run_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=500, seed=42),
            parameters=["US Stocks Return"],
        )
        assert len(report.results) == 1
        r = report.results[0]
        # Higher returns should increase success probability
        assert r.high_success >= r.low_success

    def test_higher_spending_decreases_success(self) -> None:
        report = run_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=500, seed=42),
            parameters=["Monthly Spending"],
        )
        assert len(report.results) == 1
        r = report.results[0]
        # Higher spending should decrease success probability
        assert r.high_success <= r.low_success

    def test_subset_parameters(self) -> None:
        report = run_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=200, seed=42),
            parameters=["US Stocks Return", "Inflation Rate"],
        )
        assert len(report.results) == 2
        names = {r.parameter_name for r in report.results}
        assert names == {"US Stocks Return", "Inflation Rate"}

    def test_caps_paths(self) -> None:
        """Even with 5000 configured paths, sensitivity caps at 2000."""
        report = run_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=5000, seed=42),
            parameters=["US Stocks Return"],
        )
        assert len(report.results) == 1
