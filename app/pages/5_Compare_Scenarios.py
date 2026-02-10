"""Compare Scenarios page — side-by-side comparison of saved simulations."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Compare Scenarios — MontePlan", layout="wide")

from app.components.theme import register_theme

register_theme()

st.title("Compare Scenarios")

# Initialize saved scenarios
if "saved_scenarios" not in st.session_state:
    st.session_state["saved_scenarios"] = {}

scenarios: dict = st.session_state["saved_scenarios"]  # type: ignore[type-arg]

if not scenarios:
    st.info("No scenarios saved yet. Run a simulation on the Run & Results page and save it.")
    st.stop()

# Controls
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    selected = st.multiselect(
        "Select scenarios to compare",
        options=list(scenarios.keys()),
        default=list(scenarios.keys()),
    )
with col_ctrl2:
    if st.button("Clear All Scenarios"):
        st.session_state["saved_scenarios"] = {}
        st.rerun()

if len(selected) < 1:
    st.warning("Select at least one scenario to display.")
    st.stop()

picked = {name: scenarios[name] for name in selected}

# Side-by-side metrics table
st.subheader("Key Metrics")
cols = st.columns(len(picked))
for col, (name, data) in zip(cols, picked.items(), strict=True):
    with col:
        st.markdown(f"**{name}**")
        st.metric("Success %", f"{data['success_probability']:.1%}")
        st.metric("Median Terminal", f"${data['terminal_wealth_percentiles']['p50']:,.0f}")
        st.metric("P5 Terminal", f"${data['terminal_wealth_percentiles']['p5']:,.0f}")

# Overlay fan chart
st.subheader("Portfolio Value Over Time")
show_bands = st.checkbox("Show P25-P75 bands", value=len(picked) <= 3)

from app.components.charts import dominance_scatter, overlay_fan_chart

fig_overlay = overlay_fan_chart(picked, show_bands=show_bands)
st.plotly_chart(fig_overlay, use_container_width=True)

# Dominance scatter
if len(picked) >= 2:
    st.subheader("Dominance Analysis")
    fig_dom = dominance_scatter(picked)
    st.plotly_chart(fig_dom, use_container_width=True)
