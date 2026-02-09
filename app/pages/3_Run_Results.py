"""Run & Results page — execute simulation and display results."""

from __future__ import annotations

import json

import streamlit as st

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
from monteplan.core.engine import SimulationResult, simulate
from monteplan.io.serialize import dump_config, dump_results_summary

st.set_page_config(page_title="Run & Results — MontePlan", layout="wide")
st.title("Run & Results")


@st.cache_data(show_spinner="Running simulation...")
def run_simulation(
    plan_json: str,
    market_json: str,
    policies_json: str,
    sim_json: str,
) -> dict:  # type: ignore[type-arg]
    """Run simulation with JSON-serialized configs for caching."""
    plan = PlanConfig.model_validate_json(plan_json)
    market = MarketAssumptions.model_validate_json(market_json)
    policies = PolicyBundle.model_validate_json(policies_json)
    sim_config = SimulationConfig.model_validate_json(sim_json)

    result = simulate(plan, market, policies, sim_config)

    # Convert to serializable dict for caching
    return {
        "success_probability": result.success_probability,
        "terminal_wealth_percentiles": result.terminal_wealth_percentiles,
        "wealth_time_series": {k: v.tolist() for k, v in result.wealth_time_series.items()},
        "n_paths": result.n_paths,
        "n_steps": result.n_steps,
        "seed": result.seed,
        "plan_current_age": plan.current_age,
        "plan_retirement_age": plan.retirement_age,
        "plan_end_age": plan.end_age,
    }


# Get configs from session state
plan: PlanConfig = st.session_state.get("plan", default_plan())
market: MarketAssumptions = st.session_state.get("market", default_market())
policies: PolicyBundle = st.session_state.get("policies", default_policies())
sim_config: SimulationConfig = st.session_state.get("sim_config", default_sim_config())

# Show current config summary
with st.expander("Current Configuration"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Ages:** {plan.current_age} → {plan.retirement_age} → {plan.end_age}")
        st.write(f"**Monthly Spending:** ${plan.monthly_spending:,.0f}")
        st.write(f"**Accounts:** {len(plan.accounts)}")
    with col2:
        st.write(f"**Paths:** {sim_config.n_paths:,}")
        st.write(f"**Seed:** {sim_config.seed}")
        st.write(f"**Spending Policy:** {policies.spending.policy_type}")

if st.button("Run Simulation", type="primary"):
    # Serialize configs for cache key
    result_data = run_simulation(
        plan.model_dump_json(),
        market.model_dump_json(),
        policies.model_dump_json(),
        sim_config.model_dump_json(),
    )
    st.session_state["result_data"] = result_data

if "result_data" in st.session_state:
    data = st.session_state["result_data"]

    # Metric tiles
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Success Probability", f"{data['success_probability']:.1%}")
    with col2:
        st.metric("Median Terminal Wealth", f"${data['terminal_wealth_percentiles']['p50']:,.0f}")
    with col3:
        st.metric("P5 Terminal Wealth", f"${data['terminal_wealth_percentiles']['p5']:,.0f}")
    with col4:
        st.metric("P95 Terminal Wealth", f"${data['terminal_wealth_percentiles']['p95']:,.0f}")

    # Fan chart
    st.subheader("Portfolio Value Over Time")
    from app.components.charts import fan_chart
    from monteplan.core.engine import SimulationResult as _SR

    import numpy as np

    # Reconstruct enough of SimulationResult for the chart
    class _ChartResult:
        def __init__(self, d: dict) -> None:  # type: ignore[type-arg]
            self.wealth_time_series = {k: np.array(v) for k, v in d["wealth_time_series"].items()}

            class _Plan:
                def __init__(self, d: dict) -> None:  # type: ignore[type-arg]
                    self.current_age = d["plan_current_age"]
                    self.retirement_age = d["plan_retirement_age"]
                    self.end_age = d["plan_end_age"]

            self.plan = _Plan(d)

    chart_result = _ChartResult(data)
    fig = fan_chart(chart_result)  # type: ignore[arg-type]
    st.plotly_chart(fig, use_container_width=True)

    # Downloads
    st.subheader("Export")
    col1, col2 = st.columns(2)
    with col1:
        config_json = dump_config(plan, market, policies, sim_config)
        st.download_button(
            "Download Config (JSON)",
            data=config_json,
            file_name="monteplan_config.json",
            mime="application/json",
        )
    with col2:
        results_json = dump_results_summary(
            data["success_probability"],
            data["terminal_wealth_percentiles"],
            data["n_paths"],
            data["n_steps"],
            data["seed"],
        )
        st.download_button(
            "Download Results (JSON)",
            data=results_json,
            file_name="monteplan_results.json",
            mime="application/json",
        )
