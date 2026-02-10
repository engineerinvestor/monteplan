# Guardrails vs Constant Spending

A head-to-head comparison of the two most popular retirement spending strategies.

## The Strategies

### Constant Real Spending (4% Rule)

Withdraw a fixed real dollar amount each month, adjusted only for inflation. Simple, predictable, and the baseline for most retirement planning discussions.

### Guyton-Klinger Guardrails

Start with an initial withdrawal rate, then adjust spending up or down based on portfolio performance:

- **Prosperity rule:** If the current withdrawal rate falls well below the initial rate (portfolio grew), raise spending
- **Capital preservation rule:** If the rate rises well above the initial rate (portfolio shrank), cut spending

## Setup

For a fair comparison, both strategies use the same plan, market, and simulation parameters. The guardrails policy starts with a 5% initial withdrawal rate, and the constant real policy uses the plan's `monthly_spending`.

## Results Summary

| Metric | Constant Real | Guardrails |
|---|---|---|
| Success rate | Lower | Higher |
| Spending stability | Constant (by design) | Variable (bounded) |
| Worst-case spending | Unchanged until ruin | Reduced (preservation rule) |
| Best-case spending | Unchanged | Increased (prosperity rule) |
| Terminal wealth (median) | Moderate | Higher |

## When to Use Each

### Choose Constant Real When:

- You value spending predictability above all else
- You have other income sources (Social Security, pension) that cover base needs
- Your withdrawal rate is well below 4% (large safety margin)
- You prefer simplicity in implementation

### Choose Guardrails When:

- You have a long retirement (35+ years, e.g., FIRE)
- You can tolerate spending adjustments of 10-20%
- You want to maximize the probability of portfolio survival
- You're willing to accept lower spending in bad markets in exchange for higher spending in good ones

## The No-Free-Lunch Principle

Guardrails achieve higher success rates by trading spending stability for adaptivity. When the market drops, guardrails cut spending to preserve the portfolio. When the market soars, guardrails raise spending to enjoy the surplus. Constant real spending does neither -- it maintains the same withdrawal regardless of portfolio performance.

The "cost" of guardrails is spending volatility. In the worst-case scenarios, a retiree using guardrails might need to reduce monthly spending by 10% or more. For someone with a tight budget and no other income sources, this flexibility may not be available.

## Parameter Sensitivity

The guardrails strategy is sensitive to its configuration parameters:

| Parameter | Effect of Increasing |
|---|---|
| `initial_withdrawal_rate` | Higher spending but lower success |
| `upper_threshold` | Less frequent raises, more conservative |
| `lower_threshold` | Less frequent cuts, more aggressive |
| `raise_pct` | Larger spending increases when triggered |
| `cut_pct` | Larger spending cuts when triggered |

A common mistake is setting thresholds too tight (e.g., 5%), which triggers frequent small adjustments that feel like constant tinkering. Wider thresholds (15-25%) trigger less often but with larger adjustments, which is generally preferred.

## Try It Yourself

Run the [Spending Policies notebook](../notebooks/index.md) to compare all 5 strategies side-by-side with your own plan parameters.
