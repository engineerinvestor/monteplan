"""Chart components for the Streamlit app."""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from app.components.theme import (
    COLOR_SEQUENCE,
    RUIN_COLOR,
    SPENDING_COLOR,
    WEALTH_COLOR,
    _make_rgba,
    add_retirement_vline,
    add_zero_wealth_hline,
    wealth_band_colors,
)
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

    colors = wealth_band_colors(WEALTH_COLOR)
    fig = go.Figure()

    # P5-P95 band
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([ts["p95"], ts["p5"][::-1]]),
            fill="toself",
            fillcolor=colors["outer_fill"],
            line=dict(color=colors["transparent"]),
            name="5th-95th Percentile",
            showlegend=True,
            hovertemplate="<b>%{y:$,.0f}</b><extra>P5-P95</extra>",
        )
    )

    # P25-P75 band
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([ts["p75"], ts["p25"][::-1]]),
            fill="toself",
            fillcolor=colors["inner_fill"],
            line=dict(color=colors["transparent"]),
            name="25th-75th Percentile",
            showlegend=True,
            hovertemplate="<b>%{y:$,.0f}</b><extra>P25-P75</extra>",
        )
    )

    # Median line
    fig.add_trace(
        go.Scatter(
            x=ages,
            y=ts["p50"],
            mode="lines",
            line=dict(color=WEALTH_COLOR, width=2),
            name="Median (P50)",
            hovertemplate="<b>%{y:$,.0f}</b><extra>Median</extra>",
        )
    )

    # Mean line
    if "mean" in ts:
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=ts["mean"],
                mode="lines",
                line=dict(color=WEALTH_COLOR, width=1, dash="dot"),
                name="Mean",
                hovertemplate="<b>%{y:$,.0f}</b><extra>Mean</extra>",
            )
        )

    add_retirement_vline(fig, result.plan.retirement_age)
    add_zero_wealth_hline(fig)

    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        height=500,
    )

    return fig


def spending_fan_chart(
    spending_ts: dict[str, Any],
    current_age: int,
    end_age: int,
    retirement_age: int,
) -> go.Figure:
    """Create a fan chart showing spending percentile bands over time."""
    n_points = len(spending_ts["p50"])
    ages = np.linspace(current_age, end_age, n_points + 1)[:-1]  # n_steps points

    p50 = np.array(spending_ts["p50"])
    colors = wealth_band_colors(SPENDING_COLOR)
    fig = go.Figure()

    # P5-P95 band
    p5 = np.array(spending_ts["p5"])
    p95 = np.array(spending_ts["p95"])
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([p95, p5[::-1]]),
            fill="toself",
            fillcolor=colors["outer_fill"],
            line=dict(color=colors["transparent"]),
            name="5th-95th Percentile",
            showlegend=True,
            hovertemplate="<b>%{y:$,.0f}</b><extra>P5-P95</extra>",
        )
    )

    # P25-P75 band
    p25 = np.array(spending_ts["p25"])
    p75 = np.array(spending_ts["p75"])
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ages, ages[::-1]]),
            y=np.concatenate([p75, p25[::-1]]),
            fill="toself",
            fillcolor=colors["inner_fill"],
            line=dict(color=colors["transparent"]),
            name="25th-75th Percentile",
            showlegend=True,
            hovertemplate="<b>%{y:$,.0f}</b><extra>P25-P75</extra>",
        )
    )

    # Median line
    fig.add_trace(
        go.Scatter(
            x=ages,
            y=p50,
            mode="lines",
            line=dict(color=SPENDING_COLOR, width=2),
            name="Median (P50)",
            hovertemplate="<b>%{y:$,.0f}</b><extra>Median</extra>",
        )
    )

    # Mean line
    if "mean" in spending_ts:
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=np.array(spending_ts["mean"]),
                mode="lines",
                line=dict(color=SPENDING_COLOR, width=1, dash="dot"),
                name="Mean",
                hovertemplate="<b>%{y:$,.0f}</b><extra>Mean</extra>",
            )
        )

    add_retirement_vline(fig, retirement_age)
    add_zero_wealth_hline(fig)

    fig.update_layout(
        title="Monthly Spending Over Time",
        xaxis_title="Age",
        yaxis_title="Monthly Spending ($)",
        height=400,
    )

    return fig


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
        color = COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)]
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
            fig.add_trace(
                go.Scatter(
                    x=np.concatenate([ages, ages[::-1]]),
                    y=np.concatenate([p75, p25[::-1]]),
                    fill="toself",
                    fillcolor=_make_rgba(color, 0.10),
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
                hovertemplate="<b>%{y:$,.0f}</b><extra>" + name + "</extra>",
            )
        )

    # Retirement line from first scenario
    if scenarios:
        first = next(iter(scenarios.values()))
        add_retirement_vline(fig, first["plan_retirement_age"])

    fig.update_layout(
        title="Scenario Comparison - Portfolio Value Over Time",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
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
    colors = [COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)] for i in range(len(names))]

    fig.add_trace(
        go.Scatter(
            x=success_probs,
            y=median_terminal,
            mode="markers+text",
            marker=dict(
                size=16,
                color=colors,
                line=dict(width=2, color="white"),
            ),
            text=names,
            textposition="top center",
            showlegend=False,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Success: %{x:.1f}%<br>"
                "Terminal Wealth: %{y:$,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Scenario Dominance - Success vs Terminal Wealth",
        xaxis_title="Success Probability (%)",
        yaxis_title="Median Terminal Wealth ($)",
        height=450,
    )
    return fig


def ruin_curve_chart(
    ages: list[float],
    ruin_fractions: list[float],
) -> go.Figure:
    """Create a ruin probability curve by age.

    Args:
        ages: Array of ages.
        ruin_fractions: Fraction of paths depleted at each age.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ages,
            y=[f * 100 for f in ruin_fractions],
            mode="lines",
            fill="tozeroy",
            fillcolor=_make_rgba(RUIN_COLOR, 0.15),
            line=dict(color=RUIN_COLOR, width=2),
            name="Ruin Probability",
            hovertemplate="%{y:.1f}% at age %{x:.1f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Ruin Probability by Age",
        xaxis_title="Age",
        yaxis_title="Cumulative Ruin Probability (%)",
        yaxis_range=[0, 100],
        yaxis_tickformat=".0f",
        height=400,
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

    # Decrease bars (red)
    fig.add_trace(
        go.Bar(
            y=names,
            x=low_deltas,
            orientation="h",
            name="Decrease",
            marker_color=RUIN_COLOR,
        )
    )

    # Increase bars (blue)
    fig.add_trace(
        go.Bar(
            y=names,
            x=high_deltas,
            orientation="h",
            name="Increase",
            marker_color=WEALTH_COLOR,
        )
    )

    fig.update_layout(
        title="Sensitivity Tornado - Impact on Success Probability",
        xaxis_title="Change in Success Probability (pp)",
        yaxis_tickformat="",
        barmode="overlay",
        height=max(350, 50 * len(names)),
    )
    # Add vertical line at zero with base annotation
    fig.add_vline(x=0, line_dash="solid", line_color="gray", line_width=1)
    fig.add_annotation(
        x=0,
        y=1.08,
        yref="paper",
        text=f"Base: {base_success:.1%}",
        showarrow=False,
        font=dict(size=11, color="#757575"),
    )

    return fig


# --- New chart types ---


def terminal_wealth_histogram(
    terminal_values: list[float],
    percentiles: dict[str, float],
) -> go.Figure:
    """Histogram of terminal wealth across simulation paths.

    Args:
        terminal_values: Terminal wealth for each path.
        percentiles: Dict with p5, p10, p25, p50, p75, p90, p95 keys.

    Returns:
        Plotly Figure.
    """
    vals = np.array(terminal_values)
    survived = vals[vals > 0].tolist()
    depleted = vals[vals <= 0].tolist()

    fig = go.Figure()

    if survived:
        fig.add_trace(
            go.Histogram(
                x=survived,
                name="Survived",
                marker_color=_make_rgba(SPENDING_COLOR, 0.7),
                nbinsx=60,
            )
        )

    if depleted:
        fig.add_trace(
            go.Histogram(
                x=depleted,
                name="Depleted",
                marker_color=_make_rgba(RUIN_COLOR, 0.7),
                nbinsx=20,
            )
        )

    # Percentile vertical lines
    line_specs = [
        ("p10", "dash", "#757575"),
        ("p50", "solid", WEALTH_COLOR),
        ("p90", "dash", "#757575"),
    ]
    for key, dash, color in line_specs:
        if key in percentiles:
            fig.add_vline(
                x=percentiles[key],
                line_dash=dash,
                line_color=color,
                line_width=1.5,
                annotation_text=f"{key.upper()}: ${percentiles[key]:,.0f}",
                annotation_font_size=10,
                annotation_font_color=color,
            )

    # Mean dashed line
    mean_val = np.mean(vals)
    fig.add_vline(
        x=mean_val,
        line_dash="dashdot",
        line_color="#F58231",
        line_width=1.5,
        annotation_text=f"Mean: ${mean_val:,.0f}",
        annotation_font_size=10,
        annotation_font_color="#F58231",
        annotation_position="top left",
    )

    fig.update_layout(
        title="Terminal Wealth Distribution",
        xaxis_title="Terminal Wealth ($)",
        xaxis_tickformat="$,.0f",
        yaxis_title="Count",
        yaxis_tickformat=",.0f",
        barmode="overlay",
        height=400,
    )

    return fig


def spaghetti_chart(
    sample_paths: list[list[float]],
    sample_labels: list[str],
    current_age: int,
    end_age: int,
    retirement_age: int,
) -> go.Figure:
    """Sample path spaghetti plot with highlighted special paths.

    Args:
        sample_paths: List of wealth paths (each a list of floats).
        sample_labels: Label for each path ("random", "median", "best", "worst").
        current_age: Plan start age.
        end_age: Plan end age.
        retirement_age: Retirement age for vline.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()
    n_points = len(sample_paths[0]) if sample_paths else 0
    ages = np.linspace(current_age, end_age, n_points)

    style_map: dict[str, dict[str, Any]] = {
        "random": {
            "color": _make_rgba("#9E9E9E", 0.35),
            "width": 0.8,
            "dash": "solid",
            "showlegend": False,
        },
        "median": {
            "color": WEALTH_COLOR,
            "width": 2.5,
            "dash": "solid",
            "showlegend": True,
        },
        "best": {
            "color": SPENDING_COLOR,
            "width": 2,
            "dash": "dash",
            "showlegend": True,
        },
        "worst": {
            "color": RUIN_COLOR,
            "width": 2,
            "dash": "dash",
            "showlegend": True,
        },
    }

    # Add random paths first (background)
    for i, (path, label) in enumerate(zip(sample_paths, sample_labels, strict=True)):
        style = style_map.get(label, style_map["random"])
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=path,
                mode="lines",
                line=dict(color=style["color"], width=style["width"], dash=style["dash"]),
                name=label.title() if style["showlegend"] else f"Path {i}",
                showlegend=style["showlegend"],
                hovertemplate="<b>%{y:$,.0f}</b><extra>" + label.title() + "</extra>",
            )
        )

    add_retirement_vline(fig, retirement_age)
    add_zero_wealth_hline(fig)

    fig.update_layout(
        title="Individual Simulation Paths",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        height=500,
    )

    return fig


def allocation_area_chart(
    assets: list[dict[str, Any]],
    glide_path: dict[str, Any] | None,
    current_age: int,
    end_age: int,
) -> go.Figure:
    """Stacked area chart of asset allocation over time.

    Args:
        assets: List of dicts with 'name' and 'weight' keys.
        glide_path: Optional dict with start_age, start_weights, end_age, end_weights.
        current_age: Start age for x-axis.
        end_age: End age for x-axis.

    Returns:
        Plotly Figure.
    """
    n_points = end_age - current_age + 1
    age_range = np.arange(current_age, end_age + 1)
    n_assets = len(assets)

    # Build weight matrix (n_points, n_assets)
    weights = np.zeros((n_points, n_assets))

    if glide_path is not None:
        gp_start = glide_path["start_age"]
        gp_end = glide_path["end_age"]
        start_w = np.array(glide_path["start_weights"])
        end_w = np.array(glide_path["end_weights"])

        for i, age in enumerate(age_range):
            if age <= gp_start:
                weights[i] = start_w
            elif age >= gp_end:
                weights[i] = end_w
            else:
                frac = (age - gp_start) / (gp_end - gp_start)
                weights[i] = start_w + frac * (end_w - start_w)
    else:
        # Constant allocation
        static_weights = np.array([a["weight"] for a in assets])
        weights[:] = static_weights

    fig = go.Figure()

    for j in range(n_assets):
        fig.add_trace(
            go.Scatter(
                x=age_range,
                y=weights[:, j] * 100,
                mode="lines",
                name=assets[j]["name"],
                stackgroup="one",
                line=dict(width=0.5, color=COLOR_SEQUENCE[j % len(COLOR_SEQUENCE)]),
                fillcolor=_make_rgba(COLOR_SEQUENCE[j % len(COLOR_SEQUENCE)], 0.6),
                hovertemplate="%{y:.1f}%<extra>" + assets[j]["name"] + "</extra>",
            )
        )

    fig.update_layout(
        title="Asset Allocation Over Time",
        xaxis_title="Age",
        yaxis_title="Allocation (%)",
        yaxis_range=[0, 100],
        yaxis_tickformat=".0f",
        yaxis_ticksuffix="%",
        height=350,
    )

    return fig


def sensitivity_heatmap(heatmap_data: dict[str, Any]) -> go.Figure:
    """2D sensitivity heatmap of success probability.

    Args:
        heatmap_data: Dict with keys: x_param_name, y_param_name,
            x_values, y_values, success_grid, base_x_value, base_y_value,
            base_success.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    # Heatmap
    fig.add_trace(
        go.Heatmap(
            z=heatmap_data["success_grid"],
            x=heatmap_data["x_values"],
            y=heatmap_data["y_values"],
            colorscale=[
                [0.0, RUIN_COLOR],
                [0.5, "#FFD700"],
                [1.0, SPENDING_COLOR],
            ],
            zmin=0,
            zmax=100,
            colorbar=dict(title="Success<br>Probability", ticksuffix="%"),
            hovertemplate=("%{x:.2f} / %{y:.2f}<br>Success: %{z:.1f}%<extra></extra>"),
        )
    )

    # Current plan marker
    fig.add_trace(
        go.Scatter(
            x=[heatmap_data["base_x_value"]],
            y=[heatmap_data["base_y_value"]],
            mode="markers",
            marker=dict(
                symbol="star",
                size=16,
                color="white",
                line=dict(width=2, color="black"),
            ),
            name=f"Current Plan ({heatmap_data['base_success']:.0f}%)",
            hovertemplate=(
                f"Current Plan<br>Success: {heatmap_data['base_success']:.1f}%<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="2D Sensitivity - Success Probability",
        xaxis_title=heatmap_data["x_param_name"],
        yaxis_title=heatmap_data["y_param_name"],
        yaxis_tickformat="",
        height=500,
    )

    return fig
