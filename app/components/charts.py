"""Chart components for the Streamlit app."""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from monteplan.core.engine import SimulationResult


def fan_chart(result: SimulationResult) -> go.Figure:
    """Create a fan chart showing wealth percentile bands over time."""
    ts = result.wealth_time_series
    n_points = len(ts["p50"])
    ages = np.linspace(
        result.plan.current_age,
        result.plan.end_age,
        n_points,
    )

    fig = go.Figure()

    # P5-P95 band
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([ts["p95"], ts["p5"][::-1]]),
            fill="toself",
            fillcolor="rgba(99, 110, 250, 0.1)",
            line=dict(color="rgba(99, 110, 250, 0)"),
            name="P5-P95",
            showlegend=True,
        )
    )

    # P25-P75 band
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([ts["p75"], ts["p25"][::-1]]),
            fill="toself",
            fillcolor="rgba(99, 110, 250, 0.25)",
            line=dict(color="rgba(99, 110, 250, 0)"),
            name="P25-P75",
            showlegend=True,
        )
    )

    # Median line
    fig.add_trace(
        go.Scatter(
            x=ages,
            y=ts["p50"],
            mode="lines",
            line=dict(color="rgb(99, 110, 250)", width=2),
            name="Median (P50)",
        )
    )

    # Mean line
    if "mean" in ts:
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=ts["mean"],
                mode="lines",
                line=dict(color="rgb(99, 110, 250)", width=1, dash="dot"),
                name="Mean",
            )
        )

    # Retirement line
    fig.add_vline(
        x=result.plan.retirement_age,
        line_dash="dash",
        line_color="gray",
        annotation_text="Retirement",
    )

    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )

    return fig


# Color palette for multiple scenarios
_SCENARIO_COLORS = [
    "rgb(99, 110, 250)",   # blue
    "rgb(239, 85, 59)",    # red
    "rgb(0, 204, 150)",    # green
    "rgb(171, 99, 250)",   # purple
    "rgb(255, 161, 90)",   # orange
]


def overlay_fan_chart(
    scenarios: dict[str, dict[str, Any]],
    show_bands: bool = True,
) -> go.Figure:
    """Create a fan chart overlaying median lines from multiple scenarios.

    Args:
        scenarios: Maps scenario name to result_data dict (same format as
            stored in session state).
        show_bands: If True, show P25-P75 bands per scenario.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    for idx, (name, data) in enumerate(scenarios.items()):
        color = _SCENARIO_COLORS[idx % len(_SCENARIO_COLORS)]
        ts = data["wealth_time_series"]
        n_points = len(ts["p50"])
        ages = np.linspace(
            data["plan_current_age"],
            data["plan_end_age"],
            n_points,
        )

        p50 = np.array(ts["p50"])

        if show_bands and "p25" in ts and "p75" in ts:
            p25 = np.array(ts["p25"])
            p75 = np.array(ts["p75"])
            # Parse rgb to rgba for fill
            rgba = color.replace("rgb", "rgba").replace(")", ", 0.1)")
            fig.add_trace(
                go.Scatter(
                    x=np.concatenate([ages, ages[::-1]]),
                    y=np.concatenate([p75, p25[::-1]]),
                    fill="toself",
                    fillcolor=rgba,
                    line=dict(color="rgba(0,0,0,0)"),
                    name=f"{name} P25-P75",
                    showlegend=False,
                )
            )

        fig.add_trace(
            go.Scatter(
                x=ages,
                y=p50,
                mode="lines",
                line=dict(color=color, width=2),
                name=f"{name} (Median)",
            )
        )

    # Retirement line from first scenario
    if scenarios:
        first = next(iter(scenarios.values()))
        fig.add_vline(
            x=first["plan_retirement_age"],
            line_dash="dash",
            line_color="gray",
            annotation_text="Retirement",
        )

    fig.update_layout(
        title="Scenario Comparison — Portfolio Value Over Time",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )
    return fig


def dominance_scatter(scenarios: dict[str, dict[str, Any]]) -> go.Figure:
    """Scatter plot of success probability vs median terminal wealth.

    Args:
        scenarios: Maps scenario name to result_data dict.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    names = list(scenarios.keys())
    success_probs = [scenarios[n]["success_probability"] * 100 for n in names]
    median_terminal = [scenarios[n]["terminal_wealth_percentiles"]["p50"] for n in names]
    colors = [_SCENARIO_COLORS[i % len(_SCENARIO_COLORS)] for i in range(len(names))]

    fig.add_trace(
        go.Scatter(
            x=success_probs,
            y=median_terminal,
            mode="markers+text",
            marker=dict(size=14, color=colors),
            text=names,
            textposition="top center",
            showlegend=False,
        )
    )

    fig.update_layout(
        title="Scenario Dominance — Success vs Terminal Wealth",
        xaxis_title="Success Probability (%)",
        yaxis_title="Median Terminal Wealth ($)",
        yaxis_tickformat="$,.0f",
        template="plotly_white",
        height=450,
    )
    return fig


def tornado_chart(
    results: list[dict[str, Any]],
    base_success: float,
) -> go.Figure:
    """Create a tornado chart for sensitivity analysis.

    Args:
        results: List of dicts with keys: parameter_name, low_success,
            high_success, low_value, high_value.
        base_success: Base-case success probability.

    Returns:
        Plotly Figure.
    """
    # Sort by absolute impact (largest first)
    sorted_results = sorted(
        results,
        key=lambda r: abs(r["high_success"] - r["low_success"]),
        reverse=True,
    )

    names = [r["parameter_name"] for r in sorted_results]
    low_deltas = [(r["low_success"] - base_success) * 100 for r in sorted_results]
    high_deltas = [(r["high_success"] - base_success) * 100 for r in sorted_results]

    fig = go.Figure()

    # Low perturbation bars (red)
    fig.add_trace(
        go.Bar(
            y=names,
            x=low_deltas,
            orientation="h",
            name="Low Perturbation",
            marker_color="rgb(239, 85, 59)",
        )
    )

    # High perturbation bars (blue)
    fig.add_trace(
        go.Bar(
            y=names,
            x=high_deltas,
            orientation="h",
            name="High Perturbation",
            marker_color="rgb(99, 110, 250)",
        )
    )

    fig.update_layout(
        title="Sensitivity Tornado — Impact on Success Probability",
        xaxis_title="Change in Success Probability (pp)",
        barmode="overlay",
        template="plotly_white",
        height=max(350, 50 * len(names)),
    )
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="solid", line_color="gray", line_width=1)

    return fig
