"""Sensitivity Analysis page — tornado chart of parameter impacts."""

from __future__ import annotations

import streamlit as st

from monteplan.analytics.sensitivity import run_sensitivity
from monteplan.config.defaults import (
    default_market,
    default_plan,
    default_policies,
    default_sim_config,
)
from monteplan.config.schema import (
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)

st.set_page_config(page_title="Sensitivity — MontePlan", layout="wide")
st.title("Sensitivity Analysis")

# Get configs from session state
plan: PlanConfig = st.session_state.get("plan", default_plan())
market: MarketAssumptions = st.session_state.get("market", default_market())
policies: PolicyBundle = st.session_state.get("policies", default_policies())
sim_config: SimulationConfig = st.session_state.get("sim_config", default_sim_config())

# Controls
col1, col2 = st.columns(2)
with col1:
    perturbation_pct = st.slider(
        "Perturbation (%)",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        help="How much to vary each parameter (±%)",
    )

# Build default parameter list
n_assets = len(market.assets)
default_params: list[str] = []
for i in range(n_assets):
    default_params.append(f"{market.assets[i].name} Return")
    default_params.append(f"{market.assets[i].name} Volatility")
default_params.append("Inflation Rate")
default_params.append("Monthly Spending")
default_params.append("Retirement Age")
for acct in plan.accounts:
    if acct.annual_contribution > 0:
        default_params.append(f"{acct.account_type.title()} Contribution")

with col2:
    selected_params = st.multiselect(
        "Parameters to analyze",
        options=default_params,
        default=default_params,
    )

if st.button("Run Sensitivity Analysis", type="primary"):
    with st.spinner("Running sensitivity analysis..."):
        report = run_sensitivity(
            plan,
            market,
            policies,
            sim_config,
            perturbation_pct=perturbation_pct / 100.0,
            parameters=selected_params if selected_params else None,
        )
    st.session_state["sensitivity_report"] = report

if "sensitivity_report" in st.session_state:
    report = st.session_state["sensitivity_report"]

    st.subheader("Tornado Chart")
    st.write(f"Base Success Probability: **{report.base_success_probability:.1%}**")

    from app.components.charts import tornado_chart

    chart_data = [
        {
            "parameter_name": r.parameter_name,
            "low_success": r.low_success,
            "high_success": r.high_success,
            "low_value": r.low_value,
            "high_value": r.high_value,
        }
        for r in report.results
    ]
    fig = tornado_chart(chart_data, report.base_success_probability)
    st.plotly_chart(fig, use_container_width=True)

    # Detail table
    st.subheader("Detail Table")
    table_data = []
    for r in sorted(report.results, key=lambda x: abs(x.impact), reverse=True):
        table_data.append(
            {
                "Parameter": r.parameter_name,
                "Base Value": f"{r.base_value:.4f}",
                "Low Value": f"{r.low_value:.4f}",
                "High Value": f"{r.high_value:.4f}",
                "Low Success": f"{r.low_success:.1%}",
                "High Success": f"{r.high_success:.1%}",
                "Impact (pp)": f"{r.impact * 100:+.1f}",
            }
        )
    st.table(table_data)
