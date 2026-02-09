"""Reusable form components for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from monteplan.config.schema import AccountConfig


def account_form(index: int, account: AccountConfig) -> AccountConfig:
    """Render a form for a single account and return updated config."""
    col1, col2, col3 = st.columns(3)
    with col1:
        account_type = st.selectbox(
            "Type",
            ["taxable", "traditional", "roth"],
            index=["taxable", "traditional", "roth"].index(account.account_type),
            key=f"acct_type_{index}",
        )
    with col2:
        balance = st.number_input(
            "Balance ($)",
            min_value=0.0,
            value=account.balance,
            step=10_000.0,
            key=f"acct_bal_{index}",
        )
    with col3:
        annual_contribution = st.number_input(
            "Annual Contribution ($)",
            min_value=0.0,
            value=account.annual_contribution,
            step=1_000.0,
            key=f"acct_contrib_{index}",
        )
    return AccountConfig(
        account_type=account_type,
        balance=balance,
        annual_contribution=annual_contribution,
    )
