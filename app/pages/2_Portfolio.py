"""Portfolio page — asset allocation, market assumptions, return model, stress scenarios."""

from __future__ import annotations

import streamlit as st

from monteplan.config.defaults import default_market, default_sim_config
from monteplan.config.schema import (
    AssetClass,
    GlidePath,
    MarketAssumptions,
    SimulationConfig,
    StressScenario,
)

st.set_page_config(page_title="Portfolio — MontePlan", layout="wide")
st.title("Portfolio & Assumptions")

# Initialize defaults
if "market" not in st.session_state:
    st.session_state["market"] = default_market()
if "sim_config" not in st.session_state:
    st.session_state["sim_config"] = default_sim_config()

market: MarketAssumptions = st.session_state["market"]
sim_config: SimulationConfig = st.session_state["sim_config"]

# --- Asset Allocation ---
st.subheader("Asset Allocation")
stock_weight = st.slider(
    "Stock Allocation (%)",
    min_value=0,
    max_value=100,
    value=int(market.assets[0].weight * 100) if market.assets else 70,
    step=5,
)
bond_weight = 100 - stock_weight
st.write(f"Bond Allocation: {bond_weight}%")

# Glide Path
use_glide = st.checkbox(
    "Enable Glide Path (age-based allocation shift)",
    value=market.glide_path is not None,
)
gp_start_age = 30
gp_end_age = 70
gp_end_stock = 40
if use_glide:
    col1, col2, col3 = st.columns(3)
    with col1:
        gp_start_age = st.number_input(
            "Glide Start Age", min_value=18, max_value=120,
            value=market.glide_path.start_age if market.glide_path else 30,
        )
    with col2:
        gp_end_age = st.number_input(
            "Glide End Age", min_value=gp_start_age + 1, max_value=120,
            value=market.glide_path.end_age if market.glide_path else 70,
        )
    with col3:
        gp_end_stock = st.slider(
            "End Stock Allocation (%)",
            min_value=0, max_value=100, step=5,
            value=int(market.glide_path.end_weights[0] * 100) if market.glide_path else 40,
        )
    st.caption(
        f"Allocation shifts from {stock_weight}% stocks at age {gp_start_age} "
        f"to {gp_end_stock}% stocks at age {gp_end_age}"
    )

# --- Market Assumptions ---
with st.expander("Market Assumptions", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        stock_return = st.number_input(
            "Expected Stock Return (%/yr)",
            value=market.expected_annual_returns[0] * 100,
            step=0.5,
        )
        stock_vol = st.number_input(
            "Stock Volatility (%/yr)",
            value=market.annual_volatilities[0] * 100,
            step=1.0,
        )
    with col2:
        bond_return = st.number_input(
            "Expected Bond Return (%/yr)",
            value=market.expected_annual_returns[1] * 100,
            step=0.5,
        )
        bond_vol = st.number_input(
            "Bond Volatility (%/yr)",
            value=market.annual_volatilities[1] * 100,
            step=0.5,
        )

    correlation = st.number_input(
        "Stock-Bond Correlation",
        min_value=-1.0,
        max_value=1.0,
        value=market.correlation_matrix[0][1],
        step=0.1,
    )
    inflation_mean = st.number_input(
        "Long-Run Inflation (%/yr)",
        value=market.inflation_mean * 100,
        step=0.25,
    )

# --- Return Model ---
st.subheader("Return Model")
return_model_options = ["mvn", "student_t"]
return_model_labels = {
    "mvn": "Multivariate Normal",
    "student_t": "Student-t (fat tails)",
}
return_model = st.selectbox(
    "Return Distribution",
    return_model_options,
    index=return_model_options.index(market.return_model) if market.return_model in return_model_options else 0,
    format_func=lambda x: return_model_labels.get(x, x),
)

degrees_of_freedom: float | None = market.degrees_of_freedom
if return_model == "student_t":
    degrees_of_freedom = st.number_input(
        "Degrees of Freedom",
        min_value=2.1,
        max_value=100.0,
        value=market.degrees_of_freedom or 5.0,
        step=0.5,
        help="Lower values = fatter tails. Typical range: 4-8.",
    )

# --- Stress Scenarios ---
st.subheader("Stress Scenarios")
st.caption("Deterministic overlays that modify simulation paths for specific market conditions")

stress_options = {
    "crash": "Market Crash (-38% over 12mo, V-shaped recovery)",
    "lost_decade": "Lost Decade (near-zero real returns)",
    "high_inflation": "High Inflation (6-8% annualized)",
    "sequence_risk": "Sequence Risk (poor returns early in retirement)",
}

existing_scenarios = {s.scenario_type: s for s in sim_config.stress_scenarios}
selected_scenarios: list[StressScenario] = []

for stype, label in stress_options.items():
    existing = existing_scenarios.get(stype)
    enabled = st.checkbox(label, value=existing is not None, key=f"stress_{stype}")
    if enabled:
        col1, col2, col3 = st.columns(3)
        with col1:
            s_age = st.number_input(
                "Start Age", min_value=18.0, max_value=120.0,
                value=existing.start_age if existing else 65.0,
                step=1.0, key=f"stress_age_{stype}",
            )
        with col2:
            s_dur = st.number_input(
                "Duration (months)", min_value=1, max_value=360,
                value=existing.duration_months if existing else (12 if stype == "crash" else 120),
                key=f"stress_dur_{stype}",
            )
        with col3:
            s_sev = st.number_input(
                "Severity", min_value=0.1, max_value=3.0,
                value=existing.severity if existing else 1.0,
                step=0.1, key=f"stress_sev_{stype}",
            )
        selected_scenarios.append(StressScenario(
            name=stype, scenario_type=stype,
            start_age=s_age, duration_months=int(s_dur), severity=s_sev,
        ))

# --- Simulation Settings ---
st.subheader("Simulation Settings")
preset = st.radio(
    "Path Count",
    ["Fast (1,000)", "Balanced (5,000)", "Deep (20,000)"],
    index=1,
    horizontal=True,
)
preset_map = {"Fast (1,000)": 1000, "Balanced (5,000)": 5000, "Deep (20,000)": 20000}
n_paths = preset_map[preset]

seed = st.number_input("Random Seed", value=sim_config.seed, min_value=0)

# --- Save ---
if st.button("Save Portfolio & Settings", type="primary"):
    try:
        glide_path: GlidePath | None = None
        if use_glide:
            glide_path = GlidePath(
                start_age=int(gp_start_age),
                start_weights=[stock_weight / 100, bond_weight / 100],
                end_age=int(gp_end_age),
                end_weights=[gp_end_stock / 100, (100 - gp_end_stock) / 100],
            )

        new_market = MarketAssumptions(
            assets=[
                AssetClass(name="US Stocks", weight=stock_weight / 100),
                AssetClass(name="US Bonds", weight=bond_weight / 100),
            ],
            expected_annual_returns=[stock_return / 100, bond_return / 100],
            annual_volatilities=[stock_vol / 100, bond_vol / 100],
            correlation_matrix=[
                [1.0, correlation],
                [correlation, 1.0],
            ],
            inflation_mean=inflation_mean / 100,
            inflation_vol=market.inflation_vol,
            return_model=return_model,
            degrees_of_freedom=degrees_of_freedom if return_model == "student_t" else None,
            glide_path=glide_path,
        )
        new_sim = SimulationConfig(
            n_paths=n_paths,
            seed=int(seed),
            stress_scenarios=selected_scenarios,
        )

        st.session_state["market"] = new_market
        st.session_state["sim_config"] = new_sim
        st.success("Portfolio & settings saved!")
    except Exception as e:
        st.error(f"Validation error: {e}")
