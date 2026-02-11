"""Safe withdrawal rate finder via bisection search."""

from __future__ import annotations

from dataclasses import dataclass

from monteplan.config.schema import (
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)
from monteplan.core.engine import simulate


@dataclass(frozen=True)
class SWRResult:
    """Result of a safe withdrawal rate search."""

    max_monthly_spending: float
    annual_withdrawal_amount: float
    implied_withdrawal_rate: float  # annual / initial_portfolio
    target_success_rate: float
    achieved_success_rate: float
    iterations: int
    initial_portfolio: float


def find_safe_withdrawal_rate(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
    target_success_rate: float = 0.95,
    spending_low: float = 0.0,
    spending_high: float | None = None,
    tolerance: float = 50.0,
    max_iterations: int = 20,
) -> SWRResult:
    """Find maximum monthly spending at a target success rate.

    Uses bisection on ``plan.monthly_spending``, calling ``simulate()``
    at each step. Returns the conservative (low) bound after convergence.

    Args:
        plan: Financial plan configuration (monthly_spending will be varied).
        market: Market return and inflation assumptions.
        policies: Spending, withdrawal, and rebalancing policies.
        sim_config: Simulation execution parameters.
        target_success_rate: Minimum acceptable success probability (0-1).
        spending_low: Lower bound for monthly spending search.
        spending_high: Upper bound for monthly spending search.
            If None, defaults to 2x the plan's monthly_spending.
        tolerance: Convergence tolerance in dollars (stop when range < tolerance).
        max_iterations: Maximum bisection iterations.

    Returns:
        SWRResult with the maximum safe monthly spending and implied rate.
    """
    initial_portfolio = sum(a.balance for a in plan.accounts)

    if spending_high is None:
        spending_high = max(plan.monthly_spending * 2.0, 1000.0)

    low = spending_low
    high = spending_high
    iterations = 0

    for _ in range(max_iterations):
        iterations += 1
        mid = (low + high) / 2.0

        trial_plan = plan.model_copy(update={"monthly_spending": mid})
        result = simulate(trial_plan, market, policies, sim_config)

        if result.success_probability >= target_success_rate:
            # Can spend more — move low up
            low = mid
        else:
            # Too much spending — move high down
            high = mid

        if (high - low) < tolerance:
            break

    # Use conservative (low) bound
    safe_spending = low

    # Final verification run at the safe spending level
    final_plan = plan.model_copy(update={"monthly_spending": safe_spending})
    final_result = simulate(final_plan, market, policies, sim_config)

    annual_amount = safe_spending * 12.0
    implied_rate = annual_amount / initial_portfolio if initial_portfolio > 0 else 0.0

    return SWRResult(
        max_monthly_spending=safe_spending,
        annual_withdrawal_amount=annual_amount,
        implied_withdrawal_rate=implied_rate,
        target_success_rate=target_success_rate,
        achieved_success_rate=final_result.success_probability,
        iterations=iterations,
        initial_portfolio=initial_portfolio,
    )
