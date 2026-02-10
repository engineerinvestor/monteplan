# First Simulation

This walkthrough builds a retirement plan from scratch, runs a Monte Carlo simulation, and interprets the results.

## 1. Define Your Plan

A `PlanConfig` describes who you are and how you save and spend:

```python
from monteplan.config.schema import PlanConfig, AccountConfig

plan = PlanConfig(
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
```

**Key fields:**

- `current_age` / `retirement_age` / `end_age` -- Defines the timeline. The engine simulates monthly from now until `end_age`.
- `accounts` -- One or more investment accounts. Each has a type (`taxable`, `traditional`, or `roth`), a starting balance, and an annual contribution during working years.
- `monthly_income` -- Pre-tax income during working years.
- `monthly_spending` -- Desired spending in retirement (in today's dollars).

## 2. Set Market Assumptions

`MarketAssumptions` defines the assets, expected returns, volatilities, and correlations:

```python
from monteplan.config.schema import MarketAssumptions, AssetClass

market = MarketAssumptions(
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
```

This models a 70/30 stock/bond portfolio with 7% expected stock returns, 3% bond returns, and 3% average inflation.

## 3. Choose Policies

`PolicyBundle` controls spending behavior, rebalancing, tax model, and withdrawal ordering:

```python
from monteplan.config.schema import PolicyBundle

policies = PolicyBundle()  # defaults: constant real spending, semi-annual rebalancing, flat tax
```

The default policy uses constant real spending (the "4% rule" approach), semi-annual calendar rebalancing, and a flat 25% tax rate.

## 4. Configure the Simulation

`SimulationConfig` sets execution parameters:

```python
from monteplan.config.schema import SimulationConfig

sim_config = SimulationConfig(n_paths=5000, seed=42)
```

- `n_paths` -- Number of Monte Carlo paths (more = smoother results, slower)
- `seed` -- Random seed for reproducibility. Same seed = same results.

## 5. Run It

```python
from monteplan.core.engine import simulate

result = simulate(plan, market, policies, sim_config)
```

## 6. Interpret the Results

```python
print(f"Success probability: {result.success_probability:.1%}")
print(f"Terminal wealth percentiles:")
for key, value in result.terminal_wealth_percentiles.items():
    print(f"  {key}: ${value:,.0f}")
```

**Success probability** is the fraction of simulated paths where the portfolio never fully depleted before `end_age`. A value of 47.9% means that in about 48 out of 100 simulated futures, the plan survived.

**Terminal wealth percentiles** show the distribution of portfolio values at `end_age` across all paths:

- `p5` -- 5th percentile (worst-case scenarios)
- `p25` -- 25th percentile
- `p50` -- Median outcome
- `p75` -- 75th percentile
- `p95` -- 95th percentile (best-case scenarios)

## 7. Examine Time Series

The result includes wealth and spending percentiles at every time step:

```python
import numpy as np

# Wealth percentiles: arrays of shape (n_steps,)
median_wealth = result.wealth_time_series["p50"]
ages = np.linspace(plan.current_age, plan.end_age, len(median_wealth))

print(f"Median wealth at retirement (age {plan.retirement_age}):")
retirement_idx = int((plan.retirement_age - plan.current_age) / (plan.end_age - plan.current_age) * len(median_wealth))
print(f"  ${median_wealth[retirement_idx]:,.0f}")
```

## 8. Use Built-in Defaults

For quick experiments, use the factory functions:

```python
from monteplan.config.defaults import default_plan, default_market, default_policies, default_sim_config
from monteplan.core.engine import simulate

result = simulate(default_plan(), default_market(), default_policies(), default_sim_config())
print(f"Success: {result.success_probability:.1%}")
```

## What's Next?

- [Spending Policies](../guide/spending-policies.md) -- Compare the 5 available spending strategies
- [Return Models](../guide/return-models.md) -- Fat tails, bootstrap, regime switching
- [Sensitivity Analysis](../guide/sensitivity.md) -- Find out what matters most
- [Notebooks](../notebooks/index.md) -- Interactive tutorials in Google Colab
