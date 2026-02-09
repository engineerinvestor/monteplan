"""Portfolio page — asset allocation and market assumptions."""

from __future__ import annotations

import streamlit as st

from monteplan.config.defaults import default_market, default_policies, default_sim_config
from monteplan.config.schema import (
    AssetClass,
    MarketAssumptions,
    PolicyBundle,
    SimulationConfig,
    SpendingPolicyConfig,
)

st.set_page_config(page_title="Portfolio — MontePlan", layout="wide")
st.title("Portfolio & Assumptions")

# Initialize defaults
if "market" not in st.session_state:
    st.session_state["market"] = default_market()
if "policies" not in st.session_state:
    st.session_state["policies"] = default_policies()
if "sim_config" not in st.session_state:
    st.session_state["sim_config"] = default_sim_config()

market: MarketAssumptions = st.session_state["market"]
policies: PolicyBundle = st.session_state["policies"]
sim_config: SimulationConfig = st.session_state["sim_config"]

# Asset allocation
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

# Market assumptions in expander
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

# Spending policy
st.subheader("Spending Policy")
policy_type = st.selectbox(
    "Policy",
    ["constant_real", "percent_of_portfolio"],
    index=0 if policies.spending.policy_type == "constant_real" else 1,
)

withdrawal_rate = policies.spending.withdrawal_rate
if policy_type == "percent_of_portfolio":
    withdrawal_rate = st.number_input(
        "Annual Withdrawal Rate (%)",
        value=policies.spending.withdrawal_rate * 100,
        step=0.5,
        min_value=0.1,
        max_value=100.0,
    ) / 100

# Tax rate
tax_rate = st.number_input(
    "Effective Tax Rate (%)",
    value=policies.tax_rate * 100,
    step=1.0,
    min_value=0.0,
    max_value=100.0,
) / 100

# Simulation config
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

if st.button("Save Portfolio & Settings", type="primary"):
    try:
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
        )
        new_policies = PolicyBundle(
            spending=SpendingPolicyConfig(
                policy_type=policy_type,
                withdrawal_rate=withdrawal_rate,
            ),
            tax_rate=tax_rate,
        )
        new_sim = SimulationConfig(n_paths=n_paths, seed=int(seed))

        st.session_state["market"] = new_market
        st.session_state["policies"] = new_policies
        st.session_state["sim_config"] = new_sim
        st.success("Portfolio & settings saved!")
    except Exception as e:
        st.error(f"Validation error: {e}")
