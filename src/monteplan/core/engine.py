"""Core simulation engine — the heart of monteplan."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from monteplan.config.schema import (
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)
from monteplan.core.rng import make_rng
from monteplan.core.state import SimulationState
from monteplan.core.timeline import Timeline
from monteplan.models.inflation import OUInflationModel
from monteplan.models.returns.mvn import MultivariateNormalReturns
from monteplan.policies.contributions import apply_contributions, compute_monthly_contributions
from monteplan.policies.spending.constant_real import ConstantRealSpending
from monteplan.policies.spending.percent_of_portfolio import PercentOfPortfolioSpending
from monteplan.policies.withdrawals import withdraw


@dataclass
class SimulationResult:
    """Output of a simulation run."""

    success_probability: float
    terminal_wealth_percentiles: dict[str, float]
    wealth_time_series: dict[str, np.ndarray]
    n_paths: int
    n_steps: int
    seed: int
    plan: PlanConfig
    market: MarketAssumptions
    policies: PolicyBundle
    sim_config: SimulationConfig
    all_paths: np.ndarray | None = field(default=None, repr=False)


def simulate(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
) -> SimulationResult:
    """Run a Monte Carlo simulation.

    Args:
        plan: Financial plan configuration.
        market: Market return and inflation assumptions.
        policies: Spending, withdrawal, and rebalancing policies.
        sim_config: Simulation execution parameters.

    Returns:
        SimulationResult with success probability, percentiles, and time series.
    """
    rng = make_rng(sim_config.seed)
    n_paths = sim_config.n_paths

    # Build timeline
    timeline = Timeline.from_ages(
        plan.current_age,
        plan.retirement_age,
        plan.end_age,
        plan.income_end_age,
    )
    n_steps = timeline.n_steps

    # Pre-generate all returns and inflation upfront
    return_model = MultivariateNormalReturns(market)
    returns = return_model.sample(n_paths, n_steps, rng)  # (n_paths, n_steps, n_assets)

    inflation_model = OUInflationModel(
        theta=market.inflation_mean,
        sigma=market.inflation_vol,
    )
    inflation_rates = inflation_model.sample(n_paths, n_steps, rng)  # (n_paths, n_steps)

    # Compute portfolio-weighted blended monthly return for each path/step
    weights = np.array([a.weight for a in market.assets])
    blended_returns = (returns * weights).sum(axis=2)  # (n_paths, n_steps)

    # Initialize state
    initial_balances = [a.balance for a in plan.accounts]
    account_types: list[str] = [a.account_type for a in plan.accounts]
    state = SimulationState.initialize(n_paths, initial_balances, account_types)

    # Prepare policies
    monthly_contributions = compute_monthly_contributions(
        [a.annual_contribution for a in plan.accounts]
    )

    spending_policy: ConstantRealSpending | PercentOfPortfolioSpending
    if policies.spending.policy_type == "constant_real":
        spending_policy = ConstantRealSpending(plan.monthly_spending)
    else:
        spending_policy = PercentOfPortfolioSpending(policies.spending.withdrawal_rate)

    # Storage for wealth time series
    wealth_history = np.empty((n_paths, n_steps + 1))
    wealth_history[:, 0] = state.total_wealth

    # Main simulation loop
    for t in range(n_steps):
        state.step = t

        # 1. Apply returns to account balances
        monthly_return = blended_returns[:, t]  # (n_paths,)
        growth_factor = 1.0 + monthly_return
        state.balances *= growth_factor[:, np.newaxis]

        # Ensure no negative balances from returns
        np.maximum(state.balances, 0.0, out=state.balances)

        # 2. Update cumulative inflation
        state.cumulative_inflation *= 1.0 + inflation_rates[:, t]

        # 3. Accumulation phase: add contributions and income
        if timeline.has_income(t):
            apply_contributions(state, monthly_contributions)

        # 4. Retirement phase: compute spending, withdraw, apply taxes
        if timeline.is_retired(t):
            spending_need = spending_policy.compute(state)

            # Only withdraw for non-depleted paths
            spending_need = np.where(state.is_depleted, 0.0, spending_need)

            withdrawal_order: list[str] = list(policies.withdrawal_order)
            withdraw(
                state,
                spending_need,
                withdrawal_order,
                policies.tax_rate,
            )

        # 5. Update depletion status
        state.is_depleted = state.total_wealth <= 0.0

        # 6. Record wealth snapshot
        wealth_history[:, t + 1] = state.total_wealth

    # Compute results
    # Success = portfolio never hit zero (check all retirement steps)
    retirement_wealth = wealth_history[:, timeline.retirement_step :]
    success_mask = np.all(retirement_wealth > 0, axis=1)
    success_probability = float(success_mask.mean())

    # Terminal wealth
    terminal_wealth = wealth_history[:, -1]
    percentile_keys = [5, 25, 50, 75, 95]
    terminal_pcts = np.percentile(terminal_wealth, percentile_keys)
    terminal_wealth_percentiles = {
        f"p{p}": float(v) for p, v in zip(percentile_keys, terminal_pcts, strict=True)
    }

    # Wealth time series percentiles (for fan charts)
    wealth_ts: dict[str, np.ndarray] = {}
    for p in percentile_keys:
        wealth_ts[f"p{p}"] = np.percentile(wealth_history, p, axis=0)

    wealth_ts["mean"] = wealth_history.mean(axis=0)

    return SimulationResult(
        success_probability=success_probability,
        terminal_wealth_percentiles=terminal_wealth_percentiles,
        wealth_time_series=wealth_ts,
        n_paths=n_paths,
        n_steps=n_steps,
        seed=sim_config.seed,
        plan=plan,
        market=market,
        policies=policies,
        sim_config=sim_config,
        all_paths=wealth_history if sim_config.store_paths else None,
    )
