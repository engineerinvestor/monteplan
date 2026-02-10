# Plan Configuration

The `PlanConfig` is the foundation of every simulation. It describes who you are, how you save, and how you plan to spend.

## Basic Setup

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

## Timeline Fields

| Field | Type | Description |
|---|---|---|
| `current_age` | int (18-100) | Your current age |
| `retirement_age` | int (18-100) | Age when you stop working (must be > `current_age`) |
| `end_age` | int (18-120) | Planning horizon (must be > `retirement_age`) |
| `income_end_age` | int or None | Age when earned income stops (defaults to `retirement_age`) |

The engine simulates monthly from `current_age` to `end_age`. During working years (before `retirement_age`), contributions are made and income is earned. During retirement, spending begins.

## Account Types

Three account types with distinct tax treatment:

| Type | Tax on Contributions | Tax on Growth | Tax on Withdrawals |
|---|---|---|---|
| `taxable` | Already taxed | Capital gains tax | None (basis already taxed) |
| `traditional` | Tax-deductible | Tax-deferred | Ordinary income tax |
| `roth` | Already taxed | Tax-free | Tax-free |

```python
AccountConfig(
    account_type="traditional",  # "taxable", "traditional", or "roth"
    balance=100_000,             # Starting balance
    annual_contribution=20_000,  # Annual contribution during working years
)
```

## Income and Spending

- `monthly_income` -- Pre-tax monthly income during working years
- `monthly_spending` -- Desired monthly spending in retirement (today's dollars)
- `income_growth_rate` -- Annual real income growth rate (default: 0.0)

## Discrete Events

Model one-time financial events like home purchases, inheritances, or large medical expenses:

```python
from monteplan.config.schema import DiscreteEvent

plan = PlanConfig(
    ...,
    discrete_events=[
        DiscreteEvent(age=35, amount=-50_000, description="Home down payment"),
        DiscreteEvent(age=55, amount=100_000, description="Inheritance"),
    ],
)
```

Positive amounts are inflows; negative amounts are outflows.

## Guaranteed Income

Model Social Security, pensions, and annuities:

```python
from monteplan.config.schema import GuaranteedIncomeStream

plan = PlanConfig(
    ...,
    guaranteed_income=[
        GuaranteedIncomeStream(
            name="Social Security",
            monthly_amount=2_500,
            start_age=67,
            cola_rate=0.02,      # 2% annual cost-of-living adjustment
            end_age=None,        # Lifetime (default)
        ),
        GuaranteedIncomeStream(
            name="Pension",
            monthly_amount=1_500,
            start_age=65,
            cola_rate=0.0,       # No COLA
        ),
    ],
)
```

Guaranteed income offsets the amount that must be withdrawn from the portfolio, significantly improving success rates for retirees with Social Security or pensions.

## Quick-Start Templates

Use the built-in templates as starting points:

```python
from monteplan.config.defaults import (
    default_plan,              # 30yo, retire 65, 3 accounts
    fire_plan,                 # 30yo, retire 45, aggressive saver
    coast_fire_plan,           # 35yo, retire 60, zero contributions
    conservative_retiree_plan, # 60yo, retire 65, Social Security at 67
)
```

See the [API Reference](../api/config.md) for full field documentation.
