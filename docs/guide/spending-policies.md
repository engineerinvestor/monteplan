# Spending Policies

The spending policy determines how much to withdraw from the portfolio each month during retirement. monteplan includes five policies, each with different tradeoffs between spending stability and portfolio survival.

## Policy Comparison

| Policy | Spending Stability | Success Rate | Complexity |
|---|---|---|---|
| Constant Real | Fixed (highest stability) | Lower | Simplest |
| Percent of Portfolio | Volatile (tracks market) | Never runs out* | Simple |
| Guardrails | Adaptive (bounded changes) | Higher | Moderate |
| VPW | Adaptive (actuarial) | Higher | Moderate |
| Floor and Ceiling | Bounded adaptive | Moderate | Moderate |

*Percent-of-portfolio never fully depletes but spending can drop to near-zero.

## Constant Real (4% Rule)

Withdraw a fixed real dollar amount each month, adjusted only for inflation. This is the classic "4% rule" approach.

```python
from monteplan.config.schema import PolicyBundle, SpendingPolicyConfig

policies = PolicyBundle(
    spending=SpendingPolicyConfig(policy_type="constant_real"),
)
```

The monthly withdrawal is `plan.monthly_spending * cumulative_inflation`.

**Pros:** Predictable spending. Easy to plan around.
**Cons:** Ignores portfolio performance. Can deplete in bad markets or leave large surpluses in good ones.

## Percent of Portfolio

Withdraw a fixed percentage of the current portfolio value each month.

```python
policies = PolicyBundle(
    spending=SpendingPolicyConfig(
        policy_type="percent_of_portfolio",
        withdrawal_rate=0.04,  # 4% annual rate
    ),
)
```

Monthly withdrawal = `total_portfolio * withdrawal_rate / 12`.

**Pros:** Portfolio never fully depletes (withdrawals shrink with the portfolio).
**Cons:** Spending is volatile. In a crash, spending drops sharply.

## Guyton-Klinger Guardrails

Starts with an initial withdrawal rate, then adjusts spending up or down based on how the current withdrawal rate compares to the initial rate.

```python
from monteplan.config.schema import GuardrailsConfig

policies = PolicyBundle(
    spending=SpendingPolicyConfig(
        policy_type="guardrails",
        guardrails=GuardrailsConfig(
            initial_withdrawal_rate=0.05,
            upper_threshold=0.20,   # raise spending if rate falls 20% below initial
            lower_threshold=0.20,   # cut spending if rate rises 20% above initial
            raise_pct=0.10,         # raise spending by 10%
            cut_pct=0.10,           # cut spending by 10%
        ),
    ),
)
```

**Decision rules:**

- **Prosperity rule:** If the current withdrawal rate drops more than `upper_threshold` below the initial rate (portfolio grew), raise spending by `raise_pct`.
- **Capital preservation rule:** If the current withdrawal rate rises more than `lower_threshold` above the initial rate (portfolio shrank), cut spending by `cut_pct`.

**Pros:** Adapts to market conditions. Generally higher success rates than constant real.
**Cons:** Spending changes can be abrupt. More parameters to tune.

## Variable Percentage Withdrawal (VPW)

Withdraws `1 / remaining_years` of the portfolio each month, bounded by min/max rates.

```python
from monteplan.config.schema import VPWConfig

policies = PolicyBundle(
    spending=SpendingPolicyConfig(
        policy_type="vpw",
        vpw=VPWConfig(
            min_rate=0.03,   # 3% annual floor
            max_rate=0.15,   # 15% annual ceiling
        ),
    ),
)
```

The VPW rate naturally increases with age. At age 70 with a horizon to 95, the rate would be 1/25 = 4%. At age 90, it would be 1/5 = 20% (capped by `max_rate`).

**Pros:** Actuarially sound. Naturally spends down the portfolio over the horizon.
**Cons:** Spending varies with portfolio value. Early retirement amplifies volatility.

## Floor and Ceiling

Withdraws a percentage of the portfolio, clamped between an inflation-adjusted floor and ceiling.

```python
from monteplan.config.schema import FloorCeilingConfig

policies = PolicyBundle(
    spending=SpendingPolicyConfig(
        policy_type="floor_ceiling",
        floor_ceiling=FloorCeilingConfig(
            withdrawal_rate=0.04,
            floor=3_000,      # $3,000/month minimum (today's dollars)
            ceiling=10_000,   # $10,000/month maximum (today's dollars)
        ),
    ),
)
```

**Pros:** Guarantees a minimum spending level while capping excess.
**Cons:** Floor can still trigger depletion in severe downturns.

## Configuring via PolicyBundle

The spending policy is nested inside `PolicyBundle`:

```python
policies = PolicyBundle(
    spending=SpendingPolicyConfig(
        policy_type="guardrails",
        guardrails=GuardrailsConfig(initial_withdrawal_rate=0.05),
    ),
    # Other policy settings:
    rebalancing_strategy="calendar",
    withdrawal_order=["taxable", "traditional", "roth"],
    tax_model="flat",
    tax_rate=0.22,
)
```

## Which Policy Should I Use?

- **Just getting started?** Use `constant_real` -- it's the simplest and most widely understood.
- **Worried about running out?** Try `guardrails` -- it adapts to market conditions.
- **Long retirement (FIRE)?** Consider `guardrails` or `vpw` -- they handle 40+ year horizons better.
- **Want spending guarantees?** Use `floor_ceiling` to set hard bounds.
- **Comparing strategies?** The [spending policies notebook](../notebooks/index.md) runs all five side-by-side.
