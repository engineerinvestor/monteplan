"""Plan Setup page — ages, income, spending, accounts."""

from __future__ import annotations

import streamlit as st

from monteplan.config.defaults import default_plan
from monteplan.config.schema import AccountConfig, PlanConfig

st.set_page_config(page_title="Plan Setup — MontePlan", layout="wide")
st.title("Plan Setup")

# Initialize defaults if needed
if "plan" not in st.session_state:
    st.session_state["plan"] = default_plan()

plan: PlanConfig = st.session_state["plan"]

st.subheader("Ages")
col1, col2, col3 = st.columns(3)
with col1:
    current_age = st.number_input("Current Age", min_value=18, max_value=100, value=plan.current_age)
with col2:
    retirement_age = st.number_input(
        "Retirement Age", min_value=current_age + 1, max_value=100, value=max(plan.retirement_age, current_age + 1)
    )
with col3:
    end_age = st.number_input(
        "Plan End Age", min_value=retirement_age + 1, max_value=120, value=max(plan.end_age, retirement_age + 1)
    )

st.subheader("Income & Spending")
col1, col2 = st.columns(2)
with col1:
    monthly_income = st.number_input(
        "Monthly Income ($)", min_value=0.0, value=plan.monthly_income, step=500.0
    )
with col2:
    monthly_spending = st.number_input(
        "Monthly Spending ($)", min_value=0.0, value=plan.monthly_spending, step=500.0
    )

income_end_age = st.number_input(
    "Income End Age",
    min_value=current_age,
    max_value=end_age,
    value=min(plan.income_end_age or retirement_age, end_age),
)

st.subheader("Accounts")
n_accounts = st.number_input(
    "Number of Accounts", min_value=1, max_value=10, value=len(plan.accounts)
)

accounts: list[AccountConfig] = []
for i in range(int(n_accounts)):
    existing = plan.accounts[i] if i < len(plan.accounts) else AccountConfig(
        account_type="taxable", balance=0, annual_contribution=0
    )
    with st.expander(f"Account {i + 1}: {existing.account_type.title()}", expanded=i < 3):
        from app.components.forms import account_form
        acct = account_form(i, existing)
        accounts.append(acct)

if st.button("Save Plan", type="primary"):
    try:
        new_plan = PlanConfig(
            current_age=int(current_age),
            retirement_age=int(retirement_age),
            end_age=int(end_age),
            accounts=accounts,
            monthly_income=monthly_income,
            monthly_spending=monthly_spending,
            income_end_age=int(income_end_age),
        )
        st.session_state["plan"] = new_plan
        st.success("Plan saved!")
    except Exception as e:
        st.error(f"Validation error: {e}")
