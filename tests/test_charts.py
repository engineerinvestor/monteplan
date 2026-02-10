"""Smoke tests for chart functions — each returns a go.Figure with expected traces."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import plotly.graph_objects as go
from app.components.charts import (
    allocation_area_chart,
    dominance_scatter,
    fan_chart,
    overlay_fan_chart,
    ruin_curve_chart,
    sensitivity_heatmap,
    spaghetti_chart,
    spending_fan_chart,
    terminal_wealth_histogram,
    tornado_chart,
)
from app.components.theme import register_theme

# Register theme once for all tests
register_theme()


# --- Minimal synthetic data helpers ---


@dataclass
class _MockPlan:
    current_age: int = 30
    retirement_age: int = 65
    end_age: int = 95


@dataclass
class _MockResult:
    plan: _MockPlan = field(default_factory=_MockPlan)
    wealth_time_series: dict[str, np.ndarray] = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = 100
        if not self.wealth_time_series:
            self.wealth_time_series = {
                "p5": np.linspace(100_000, 50_000, n),
                "p25": np.linspace(100_000, 80_000, n),
                "p50": np.linspace(100_000, 120_000, n),
                "p75": np.linspace(100_000, 200_000, n),
                "p95": np.linspace(100_000, 400_000, n),
                "mean": np.linspace(100_000, 150_000, n),
            }


class TestFanChart:
    def test_returns_figure(self) -> None:
        fig = fan_chart(_MockResult())  # type: ignore[arg-type]
        assert isinstance(fig, go.Figure)

    def test_trace_count(self) -> None:
        fig = fan_chart(_MockResult())  # type: ignore[arg-type]
        # P5-P95, P25-P75, median, mean = 4 traces
        assert len(fig.data) == 4

    def test_without_mean(self) -> None:
        result = _MockResult()
        del result.wealth_time_series["mean"]
        fig = fan_chart(result)  # type: ignore[arg-type]
        assert len(fig.data) == 3


class TestSpendingFanChart:
    def test_returns_figure(self) -> None:
        n = 60
        ts = {
            "p5": list(range(n)),
            "p25": list(range(n)),
            "p50": list(range(n)),
            "p75": list(range(n)),
            "p95": list(range(n)),
        }
        fig = spending_fan_chart(ts, 30, 95, 65)
        assert isinstance(fig, go.Figure)

    def test_trace_count(self) -> None:
        n = 60
        ts = {
            "p5": list(range(n)),
            "p25": list(range(n)),
            "p50": list(range(n)),
            "p75": list(range(n)),
            "p95": list(range(n)),
        }
        fig = spending_fan_chart(ts, 30, 95, 65)
        # P5-P95, P25-P75, median = 3 traces
        assert len(fig.data) == 3


class TestOverlayFanChart:
    def test_returns_figure(self) -> None:
        scenario = {
            "wealth_time_series": {
                "p25": list(range(50)),
                "p50": list(range(50)),
                "p75": list(range(50)),
            },
            "plan_current_age": 30,
            "plan_end_age": 95,
            "plan_retirement_age": 65,
        }
        fig = overlay_fan_chart({"A": scenario, "B": scenario})
        assert isinstance(fig, go.Figure)
        # 2 scenarios × (1 band + 1 median) = 4 traces
        assert len(fig.data) == 4


class TestDominanceScatter:
    def test_returns_figure(self) -> None:
        scenarios = {
            "A": {
                "success_probability": 0.8,
                "terminal_wealth_percentiles": {"p50": 500_000},
            },
            "B": {
                "success_probability": 0.6,
                "terminal_wealth_percentiles": {"p50": 300_000},
            },
        }
        fig = dominance_scatter(scenarios)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1


class TestRuinCurve:
    def test_returns_figure(self) -> None:
        fig = ruin_curve_chart([65.0, 70.0, 80.0, 90.0], [0.0, 0.1, 0.3, 0.5])
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1


class TestTornadoChart:
    def test_returns_figure(self) -> None:
        results = [
            {
                "parameter_name": "A",
                "low_success": 0.4,
                "high_success": 0.6,
                "low_value": 0.9,
                "high_value": 1.1,
            },
            {
                "parameter_name": "B",
                "low_success": 0.45,
                "high_success": 0.55,
                "low_value": 0.9,
                "high_value": 1.1,
            },
        ]
        fig = tornado_chart(results, base_success=0.5)
        assert isinstance(fig, go.Figure)
        # 2 traces: decrease + increase bars
        assert len(fig.data) == 2


class TestTerminalWealthHistogram:
    def test_returns_figure(self) -> None:
        vals = list(np.random.default_rng(42).normal(500_000, 200_000, 1000))
        percentiles = {
            "p10": 200_000.0,
            "p50": 500_000.0,
            "p90": 800_000.0,
        }
        fig = terminal_wealth_histogram(vals, percentiles)
        assert isinstance(fig, go.Figure)
        # 1 histogram (all survived) + 0 depleted = 1 trace
        assert len(fig.data) >= 1

    def test_with_depleted_paths(self) -> None:
        vals = list(np.random.default_rng(42).normal(100_000, 300_000, 1000))
        percentiles = {
            "p10": -50_000.0,
            "p50": 100_000.0,
            "p90": 400_000.0,
        }
        fig = terminal_wealth_histogram(vals, percentiles)
        # Both survived and depleted histograms
        assert len(fig.data) >= 2


class TestSpaghettiChart:
    def test_returns_figure(self) -> None:
        paths = [list(range(50)) for _ in range(23)]
        labels = ["random"] * 20 + ["median", "best", "worst"]
        fig = spaghetti_chart(paths, labels, 30, 95, 65)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 23


class TestAllocationAreaChart:
    def test_constant_allocation(self) -> None:
        assets = [
            {"name": "Stocks", "weight": 0.7},
            {"name": "Bonds", "weight": 0.3},
        ]
        fig = allocation_area_chart(assets, None, 30, 90)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_with_glide_path(self) -> None:
        assets = [
            {"name": "Stocks", "weight": 0.7},
            {"name": "Bonds", "weight": 0.3},
        ]
        gp = {
            "start_age": 30,
            "start_weights": [0.8, 0.2],
            "end_age": 70,
            "end_weights": [0.4, 0.6],
        }
        fig = allocation_area_chart(assets, gp, 30, 90)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2


class TestSensitivityHeatmap:
    def test_returns_figure(self) -> None:
        data = {
            "x_param_name": "Monthly Spending",
            "y_param_name": "Stock Allocation",
            "x_values": [3000, 4000, 5000],
            "y_values": [0.4, 0.6, 0.8],
            "success_grid": [
                [80.0, 70.0, 60.0],
                [75.0, 65.0, 55.0],
                [70.0, 60.0, 50.0],
            ],
            "base_x_value": 4000,
            "base_y_value": 0.6,
            "base_success": 65.0,
        }
        fig = sensitivity_heatmap(data)
        assert isinstance(fig, go.Figure)
        # 1 heatmap + 1 star marker = 2 traces
        assert len(fig.data) == 2
