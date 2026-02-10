"""Chart components for the Streamlit app."""

from __future__ import annotations

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
