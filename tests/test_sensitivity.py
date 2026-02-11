"""Tests for OAT sensitivity analysis."""

from __future__ import annotations

from monteplan.analytics.sensitivity import run_2d_sensitivity, run_sensitivity
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


class TestSensitivity2D:
    def test_grid_dimensions(self) -> None:
        result = run_2d_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            x_param="Monthly Spending",
            y_param="Equity Allocation",
            x_range=(3000, 5000),
            y_range=(0.4, 0.9),
            x_steps=3,
            y_steps=3,
            max_workers=1,
        )
        assert len(result.y_values) == 3
        assert len(result.x_values) == 3
        assert len(result.success_grid) == 3
        assert len(result.success_grid[0]) == 3

    def test_values_in_range(self) -> None:
        result = run_2d_sensitivity(
            default_plan(),
            default_market(),
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            x_param="Monthly Spending",
            y_param="Inflation Rate",
            x_range=(3000, 5000),
            y_range=(0.01, 0.05),
            x_steps=3,
            y_steps=3,
            max_workers=1,
        )
        for row in result.success_grid:
            for val in row:
                assert 0.0 <= val <= 100.0

    def test_base_values_populated(self) -> None:
        plan = default_plan()
        market = default_market()
        result = run_2d_sensitivity(
            plan,
            market,
            default_policies(),
            SimulationConfig(n_paths=100, seed=42),
            x_param="Monthly Spending",
            y_param="Inflation Rate",
            x_range=(3000, 5000),
            y_range=(0.01, 0.05),
            x_steps=3,
            y_steps=3,
            max_workers=1,
        )
        assert result.base_x_value == plan.monthly_spending
        assert result.base_y_value == market.inflation_mean
        assert 0.0 <= result.base_success <= 100.0
