"""Default configuration values for monteplan."""

from __future__ import annotations

from monteplan.config.schema import (
    AccountConfig,
    AssetClass,
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)


def default_plan() -> PlanConfig:
    """Default plan: 30-year-old, retiring at 65, horizon to 95."""
    return PlanConfig(
        current_age=30,
        retirement_age=65,
        end_age=95,
        accounts=[
            AccountConfig(account_type="taxable", balance=50_000, annual_contribution=6_000),
            AccountConfig(account_type="traditional", balance=100_000, annual_contribution=20_000),
            AccountConfig(account_type="roth", balance=30_000, annual_contribution=7_000),
        ],
        monthly_income=8_000,
        monthly_spending=5_000,
    )


def default_market() -> MarketAssumptions:
    """Default 2-asset market: US stocks + US bonds."""
    return MarketAssumptions(
        assets=[
            AssetClass(name="US Stocks", weight=0.7),
            AssetClass(name="US Bonds", weight=0.3),
        ],
        expected_annual_returns=[0.07, 0.03],
        annual_volatilities=[0.16, 0.06],
        correlation_matrix=[
            [1.0, 0.0],
            [0.0, 1.0],
        ],
        inflation_mean=0.03,
        inflation_vol=0.01,
    )


def default_sim_config() -> SimulationConfig:
    """Default simulation config: 5000 paths, seed 42."""
    return SimulationConfig(n_paths=5000, seed=42)


def default_policies() -> PolicyBundle:
    """Default policies: constant real spending, semi-annual rebalancing."""
    return PolicyBundle()
