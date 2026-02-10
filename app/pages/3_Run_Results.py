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
from monteplan.analytics.metrics import max_drawdown_distribution, ruin_by_age, spending_volatility
from monteplan.core.engine import SimulationResult, simulate
from monteplan.io.serialize import dump_config, dump_results_summary, dump_time_series_csv

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

    # Enable store_paths temporarily for metrics computation
    sim_config_with_paths = SimulationConfig(
        n_paths=sim_config.n_paths,
        seed=sim_config.seed,
        store_paths=True,
        antithetic=sim_config.antithetic,
        stress_scenarios=sim_config.stress_scenarios,
    )
    result = simulate(plan, market, policies, sim_config_with_paths)

    # Compute additional metrics from raw paths
    retirement_step = (plan.retirement_age - plan.current_age) * 12
    drawdown_stats = {}
    spend_vol_stats = {}
    ruin_ages: list[float] = []
    ruin_fracs: list[float] = []

    if result.all_paths is not None:
        drawdown_stats = max_drawdown_distribution(result.all_paths)
        spend_vol_stats = spending_volatility(
            # Reconstruct spending from the spending_time_series percentiles is not exact;
            # we need the raw spending. Since we have spending_ts but not raw paths,
            # compute from wealth-based proxy. For now, use spending_ts for vol.
            # Actually, we need to pass spending_history through. Let's use the ts.
            result.all_paths[:, :0],  # placeholder
            retirement_step,
        )
        ages_arr, fracs_arr = ruin_by_age(
            result.all_paths, retirement_step, plan.current_age,
        )
        ruin_ages = ages_arr.tolist()
        ruin_fracs = fracs_arr.tolist()

    # Convert to serializable dict for caching
    return {
        "success_probability": result.success_probability,
        "terminal_wealth_percentiles": result.terminal_wealth_percentiles,
        "wealth_time_series": {k: v.tolist() for k, v in result.wealth_time_series.items()},
        "spending_time_series": {k: v.tolist() for k, v in result.spending_time_series.items()},
        "max_drawdown": drawdown_stats,
        "ruin_ages": ruin_ages,
        "ruin_fractions": ruin_fracs,
        "n_paths": result.n_paths,
        "n_steps": result.n_steps,
        "seed": result.seed,
        "config_hash": result.config_hash,
        "engine_version": result.engine_version,
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Plan**")
        st.write(f"Ages: {plan.current_age} → {plan.retirement_age} → {plan.end_age}")
        st.write(f"Monthly Spending: ${plan.monthly_spending:,.0f}")
        st.write(f"Monthly Income: ${plan.monthly_income:,.0f}")
        st.write(f"Accounts: {len(plan.accounts)}")
        if plan.income_growth_rate != 0:
            st.write(f"Income Growth: {plan.income_growth_rate:.1%}/yr")
        if plan.discrete_events:
            st.write(f"Discrete Events: {len(plan.discrete_events)}")
    with col2:
        st.markdown("**Portfolio & Market**")
        st.write(f"Allocation: {market.assets[0].weight:.0%} / {market.assets[1].weight:.0%}")
        st.write(f"Return Model: {market.return_model}")
        if market.glide_path:
            st.write(
                f"Glide Path: {market.glide_path.start_weights[0]:.0%} → "
                f"{market.glide_path.end_weights[0]:.0%} stocks"
            )
        if sim_config.stress_scenarios:
            st.write(f"Stress Scenarios: {len(sim_config.stress_scenarios)}")
    with col3:
        st.markdown("**Policies & Simulation**")
        st.write(f"Spending: {policies.spending.policy_type}")
        st.write(f"Tax Model: {policies.tax_model}")
        if policies.tax_model == "us_federal":
            st.write(f"Filing: {policies.filing_status.replace('_', ' ').title()}")
        else:
            st.write(f"Tax Rate: {policies.tax_rate:.0%}")
        st.write(f"Paths: {sim_config.n_paths:,} | Seed: {sim_config.seed}")

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

    # Spending fan chart
    if "spending_time_series" in data:
        st.subheader("Monthly Spending Over Time")
        from app.components.charts import spending_fan_chart

        spending_fig = spending_fan_chart(
            data["spending_time_series"],
            data["plan_current_age"],
            data["plan_end_age"],
            data["plan_retirement_age"],
        )
        st.plotly_chart(spending_fig, use_container_width=True)

    # Max drawdown and ruin curve
    if data.get("max_drawdown"):
        st.subheader("Risk Metrics")
        dd = data["max_drawdown"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Max Drawdown", f"{dd['p50']:.1%}")
        with col2:
            st.metric("P95 Max Drawdown", f"{dd['p95']:.1%}")
        with col3:
            st.metric("Mean Max Drawdown", f"{dd['mean']:.1%}")

    if data.get("ruin_ages") and data.get("ruin_fractions"):
        from app.components.charts import ruin_curve_chart

        ruin_fig = ruin_curve_chart(data["ruin_ages"], data["ruin_fractions"])
        st.plotly_chart(ruin_fig, use_container_width=True)

    # Simulation metadata
    with st.expander("Simulation Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Paths:** {data['n_paths']:,}")
            st.write(f"**Steps:** {data['n_steps']:,}")
            st.write(f"**Seed:** {data['seed']}")
        with col2:
            st.write(f"**Engine Version:** {data.get('engine_version', 'N/A')}")
            st.write(f"**Config Hash:** `{data.get('config_hash', 'N/A')[:12]}...`")

    # Save scenario for comparison
    st.subheader("Save for Comparison")
    scenario_name = st.text_input(
        "Scenario Name",
        value=f"Scenario {len(st.session_state.get('saved_scenarios', {})) + 1}",
        key="scenario_name_input",
    )
    if st.button("Save Scenario for Comparison"):
        if "saved_scenarios" not in st.session_state:
            st.session_state["saved_scenarios"] = {}
        st.session_state["saved_scenarios"][scenario_name] = {
            **data,
            "plan_json": plan.model_dump_json(),
            "market_json": market.model_dump_json(),
            "policies_json": policies.model_dump_json(),
            "sim_json": sim_config.model_dump_json(),
        }
        st.success(f"Scenario '{scenario_name}' saved! Go to Compare Scenarios page to view.")

    # Downloads
    st.subheader("Export")
    col1, col2, col3 = st.columns(3)
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
    with col3:
        wealth_csv = dump_time_series_csv(
            data["wealth_time_series"],
            data["plan_current_age"],
            data["plan_end_age"],
            label="Wealth",
        )
        st.download_button(
            "Download Time Series (CSV)",
            data=wealth_csv,
            file_name="monteplan_wealth_ts.csv",
            mime="text/csv",
        )
