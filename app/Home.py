"""MontePlan — Monte Carlo Financial Planning Simulator."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `from app.components...` imports work
# when Streamlit Cloud runs `streamlit run app/Home.py`.
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import streamlit as st

st.set_page_config(
    page_title="MontePlan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.theme import register_theme

register_theme()

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

st.subheader("Quick Start Templates")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Default Plan", type="primary"):
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
        st.success("Defaults loaded!")

with col2:
    if st.button("FIRE"):
        from monteplan.config.defaults import (
            default_market,
            default_policies,
            default_sim_config,
            fire_plan,
        )

        st.session_state["plan"] = fire_plan()
        st.session_state["market"] = default_market()
        st.session_state["policies"] = default_policies()
        st.session_state["sim_config"] = default_sim_config()
        st.success("FIRE template loaded!")

with col3:
    if st.button("Coast FIRE"):
        from monteplan.config.defaults import (
            coast_fire_plan,
            default_market,
            default_policies,
            default_sim_config,
        )

        st.session_state["plan"] = coast_fire_plan()
        st.session_state["market"] = default_market()
        st.session_state["policies"] = default_policies()
        st.session_state["sim_config"] = default_sim_config()
        st.success("Coast FIRE template loaded!")

with col4:
    if st.button("Conservative Retiree"):
        from monteplan.config.defaults import (
            conservative_retiree_plan,
            default_market,
            default_policies,
            default_sim_config,
        )

        st.session_state["plan"] = conservative_retiree_plan()
        st.session_state["market"] = default_market()
        st.session_state["policies"] = default_policies()
        st.session_state["sim_config"] = default_sim_config()
        st.success("Conservative Retiree template loaded!")
