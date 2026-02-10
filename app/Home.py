"""MontePlan — Monte Carlo Financial Planning Simulator."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="MontePlan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("MontePlan")
st.subheader("Monte Carlo Financial Planning Simulator")

st.markdown(
    """
    Plan your financial future with Monte Carlo simulations.
    Model accumulation and retirement with realistic assumptions
    about returns, inflation, taxes, and spending policies.

    ---

    ### How it works

    1. **Plan Setup** — Enter your age, income, spending, accounts, and life events
    2. **Portfolio** — Set asset allocation, return model, glide path, and stress scenarios
    3. **Run & Results** — Run the simulation and explore the results
    4. **Policies** — Configure spending policy, tax model, withdrawal order, and rebalancing

    ---

    ### Important Disclaimer

    This is an **educational tool** for exploring financial planning concepts.
    It is **not financial advice**. Results are simulations based on simplified
    models and assumptions. Consult a qualified financial advisor for real
    planning decisions.

    ---
    """
)

if st.button("Quick Start with Defaults", type="primary"):
    from monteplan.config.defaults import (
        default_market,
        default_plan,
        default_policies,
        default_sim_config,
    )

    st.session_state["plan"] = default_plan()
    st.session_state["market"] = default_market()
    st.session_state["policies"] = default_policies()
    st.session_state["sim_config"] = default_sim_config()
    st.success("Defaults loaded! Navigate to Plan Setup to customize, or Run & Results to simulate.")
