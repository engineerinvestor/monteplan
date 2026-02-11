#!/usr/bin/env python3
"""Generate publication-quality charts for the README.

Produces 3 PNGs in docs/images/:
  1. fan_chart.png        — Portfolio wealth percentile bands over time
  2. spending_comparison.png — Median wealth under 4 spending policies
  3. ruin_curve.png        — Cumulative ruin probability by age

Uses seed=42 for reproducibility and theme colors from app/components/theme.py.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from monteplan import default_market, default_plan, default_policies, default_sim_config, simulate
from monteplan.analytics.metrics import ruin_by_age
from monteplan.config.schema import PolicyBundle, SimulationConfig, SpendingPolicyConfig

# ---------------------------------------------------------------------------
# Theme (matching app/components/theme.py)
# ---------------------------------------------------------------------------
BLUE = "#4363D8"
GREEN = "#3CB44B"
RED = "#E6194B"
ORANGE = "#F58231"
PURPLE = "#911EB4"
GRID_COLOR = "#E5E5E5"
VLINE_COLOR = "#9E9E9E"

OUTER_ALPHA = 0.08
INNER_ALPHA = 0.22

FIGSIZE = (10, 5)
DPI = 150

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"


def _currency_formatter(x: float, _pos: object) -> str:
    """Format y-axis ticks as $K or $M."""
    if abs(x) >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x / 1_000:.0f}K"
    return f"${x:.0f}"


def _style_ax(ax: plt.Axes) -> None:
    """Apply common axis styling."""
    ax.set_facecolor("white")
    ax.grid(True, color=GRID_COLOR, alpha=0.30, linewidth=0.8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_currency_formatter))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(colors="#555555")


def _ages_from_result(result: object) -> np.ndarray:
    """Build an age array from a SimulationResult."""
    plan = result.plan  # type: ignore[attr-defined]
    n_steps = result.n_steps  # type: ignore[attr-defined]
    return np.linspace(plan.current_age, plan.end_age, n_steps + 1)


# ---------------------------------------------------------------------------
# Chart 1: Fan chart
# ---------------------------------------------------------------------------
def generate_fan_chart() -> None:
    """Hero image — percentile bands of portfolio wealth over time."""
    plan = default_plan()
    sim_cfg = default_sim_config()  # 5000 paths, seed=42

    result = simulate(plan, default_market(), default_policies(), sim_cfg)
    ts = result.wealth_time_series
    ages = _ages_from_result(result)

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")

    # P5–P95 outer band
    ax.fill_between(ages, ts["p5"], ts["p95"], color=BLUE, alpha=OUTER_ALPHA, label="P5–P95")
    # P25–P75 inner band
    ax.fill_between(ages, ts["p25"], ts["p75"], color=BLUE, alpha=INNER_ALPHA, label="P25–P75")
    # Median line
    ax.plot(ages, ts["p50"], color=BLUE, linewidth=2, label="Median")

    # Retirement vertical line
    ax.axvline(plan.retirement_age, color=VLINE_COLOR, linestyle="--", linewidth=1.5)
    ax.text(
        plan.retirement_age + 0.5,
        ax.get_ylim()[1] * 0.92,
        "Retirement",
        color="#757575",
        fontsize=10,
    )

    ax.set_xlabel("Age", fontsize=12, color="#555555")
    ax.set_ylabel("Portfolio Value", fontsize=12, color="#555555")
    ax.set_title("Monte Carlo Wealth Projection", fontsize=14, fontweight="bold", color="#333333")
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fan_chart.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {OUT_DIR / 'fan_chart.png'}")


# ---------------------------------------------------------------------------
# Chart 2: Spending policy comparison
# ---------------------------------------------------------------------------
POLICY_CONFIGS: list[tuple[str, str, SpendingPolicyConfig]] = [
    ("Constant Real", BLUE, SpendingPolicyConfig(policy_type="constant_real")),
    ("Guardrails", GREEN, SpendingPolicyConfig(policy_type="guardrails")),
    ("VPW", ORANGE, SpendingPolicyConfig(policy_type="vpw")),
    ("Floor & Ceiling", PURPLE, SpendingPolicyConfig(policy_type="floor_ceiling")),
]


def generate_spending_comparison() -> None:
    """Overlay median wealth for 4 spending policies."""
    plan = default_plan()
    market = default_market()
    sim_cfg = default_sim_config()

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")

    for label, color, spending_cfg in POLICY_CONFIGS:
        policies = PolicyBundle(spending=spending_cfg)
        result = simulate(plan, market, policies, sim_cfg)
        ages = _ages_from_result(result)
        ax.plot(ages, result.wealth_time_series["p50"], color=color, linewidth=2, label=label)

    ax.axvline(plan.retirement_age, color=VLINE_COLOR, linestyle="--", linewidth=1.5)
    ax.text(
        plan.retirement_age + 0.5,
        ax.get_ylim()[1] * 0.92,
        "Retirement",
        color="#757575",
        fontsize=10,
    )

    ax.set_xlabel("Age", fontsize=12, color="#555555")
    ax.set_ylabel("Median Portfolio Value", fontsize=12, color="#555555")
    ax.set_title("Spending Policy Comparison", fontsize=14, fontweight="bold", color="#333333")
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    _style_ax(ax)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "spending_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {OUT_DIR / 'spending_comparison.png'}")


# ---------------------------------------------------------------------------
# Chart 3: Ruin curve
# ---------------------------------------------------------------------------
def generate_ruin_curve() -> None:
    """Cumulative ruin probability by age."""
    plan = default_plan()
    sim_cfg = SimulationConfig(n_paths=5000, seed=42, store_paths=True)

    result = simulate(plan, default_market(), default_policies(), sim_cfg)
    assert result.all_paths is not None

    retirement_step = int((plan.retirement_age - plan.current_age) * 12)
    ages, ruin_fracs = ruin_by_age(result.all_paths, retirement_step, plan.current_age)

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")

    ax.fill_between(ages, 0, ruin_fracs * 100, color=RED, alpha=0.15)
    ax.plot(ages, ruin_fracs * 100, color=RED, linewidth=2, label="Ruin Probability")

    ax.set_xlabel("Age", fontsize=12, color="#555555")
    ax.set_ylabel("Cumulative Ruin Probability (%)", fontsize=12, color="#555555")
    ax.set_title("Ruin Probability by Age", fontsize=14, fontweight="bold", color="#333333")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)

    # Override y-axis formatter for percentage
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_facecolor("white")
    ax.grid(True, color=GRID_COLOR, alpha=0.30, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(colors="#555555")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "ruin_curve.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {OUT_DIR / 'ruin_curve.png'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating README charts...")
    generate_fan_chart()
    generate_spending_comparison()
    generate_ruin_curve()
    print("Done.")
