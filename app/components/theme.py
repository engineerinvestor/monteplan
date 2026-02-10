"""Custom Plotly theme for MontePlan charts."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# --- Colorblind-friendly palette (IBM/Wong-inspired) ---
WEALTH_COLOR = "#4363D8"
SPENDING_COLOR = "#3CB44B"
RUIN_COLOR = "#E6194B"

COLOR_SEQUENCE = [
    "#4363D8",  # blue
    "#E6194B",  # red
    "#3CB44B",  # green
    "#F58231",  # orange
    "#911EB4",  # purple
    "#42D4F4",  # cyan
    "#F032E6",  # magenta
    "#BFEF45",  # lime
]

# Band opacity constants
OUTER_BAND_OPACITY = 0.08
INNER_BAND_OPACITY = 0.22

# Font stack
_FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def _make_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color string to rgba() with given alpha."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def wealth_band_colors(hex_color: str) -> dict[str, str]:
    """Return fill/line colors for wealth fan chart bands."""
    return {
        "outer_fill": _make_rgba(hex_color, OUTER_BAND_OPACITY),
        "inner_fill": _make_rgba(hex_color, INNER_BAND_OPACITY),
        "transparent": _make_rgba(hex_color, 0),
        "line": hex_color,
    }


def add_retirement_vline(fig: go.Figure, age: int | float) -> None:
    """Add a styled retirement vertical line annotation."""
    fig.add_vline(
        x=age,
        line_dash="dash",
        line_color="#9E9E9E",
        line_width=1.5,
        annotation_text="Retirement",
        annotation_font_size=11,
        annotation_font_color="#757575",
    )


def add_zero_wealth_hline(fig: go.Figure) -> None:
    """Add a $0 reference horizontal line."""
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#BDBDBD",
        line_width=1,
    )


def register_theme() -> None:
    """Register and activate the monteplan Plotly template."""
    monteplan_layout = go.Layout(
        font=dict(family=_FONT_FAMILY, size=13),
        title_font=dict(size=16),
        colorway=COLOR_SEQUENCE,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            gridcolor="#E5E5E5",
            zerolinecolor="#BDBDBD",
            zerolinewidth=1,
        ),
        yaxis=dict(
            gridcolor="#E5E5E5",
            zerolinecolor="#BDBDBD",
            zerolinewidth=1,
            tickformat="$,.0f",
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=60, r=20, t=60, b=40),
    )

    pio.templates["monteplan"] = go.layout.Template(layout=monteplan_layout)
    pio.templates.default = "monteplan"
