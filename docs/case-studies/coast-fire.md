# Case Study: Coast FIRE

## Persona

**Jamie**, age 35, has accumulated $480,000 across three accounts and wants to "coast" -- stop contributing entirely and let compound growth carry the portfolio to a traditional retirement at 60.

| Parameter | Value |
|---|---|
| Current age | 35 |
| Retirement age | 60 |
| Planning horizon | to 95 |
| Monthly spending | $4,000 |
| Annual savings | $0 (coasting) |
| Current portfolio | $480,000 |
| Allocation | 70/30 stocks/bonds |

```python
from monteplan.config.defaults import coast_fire_plan
plan = coast_fire_plan()
```

## The Coast FIRE Concept

Coast FIRE means having enough invested that, even with zero additional contributions, compound growth is expected to build a sufficient retirement portfolio by a traditional retirement age. The key variable is: **is $480K at age 35 enough to coast to 60?**

## Analysis

### Growth Phase (35-60)

With 25 years of compound growth and no contributions:

- At 7% nominal stock returns and 70/30 allocation, the expected portfolio at age 60 is substantial
- But the range of outcomes is wide: good markets could double the expected value, while poor markets might barely grow the portfolio

### Spending Phase (60-95)

The 35-year retirement is shorter than the FIRE case but still longer than traditional. Key factors:

- $4,000/month spending requirement
- No guaranteed income (no Social Security modeled in the base case)
- 35 years of inflation eroding purchasing power

### Sensitivity Results

The most impactful parameters for Jamie's plan:

1. **Stock returns** -- The plan is entirely dependent on market performance since there are no contributions
2. **Monthly spending** -- Each $500/month reduction significantly improves success
3. **Inflation** -- 25+ years of compounding inflation matters enormously
4. **Retirement age** -- Delaying to 62 or 63 adds meaningful safety margin

## What If Jamie Contributes a Little?

Coast FIRE is black-and-white (contribute $0), but a "barista FIRE" approach -- contributing even $500/month from part-time work -- can dramatically improve outcomes:

```python
from monteplan.config.schema import AccountConfig

# Modify one account to add small contributions
plan_barista = plan.model_copy(update={
    "accounts": [
        AccountConfig(account_type="taxable", balance=100_000, annual_contribution=6_000),
        AccountConfig(account_type="traditional", balance=300_000, annual_contribution=0),
        AccountConfig(account_type="roth", balance=80_000, annual_contribution=0),
    ],
})
```

## Takeaways

1. **Coast FIRE works best with a large starting portfolio** -- $480K at 35 is near the edge; $600K+ provides more margin
2. **The plan is equity-dependent** -- with zero contributions, returns must do all the work
3. **Consider adding Social Security** -- even modest benefits at 67 significantly improve the post-60 phase
4. **Small contributions make a big difference** -- "barista FIRE" with even $6K/year in contributions is much more robust
5. **Inflation is the silent risk** -- 60 years of inflation (age 35-95) requires real returns to do heavy lifting
