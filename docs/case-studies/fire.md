# Case Study: FIRE at 45

!!! info "Interactive Version"
    Run this case study yourself: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/engineerinvestor/monteplan/blob/main/notebooks/04_case_study_fire.ipynb)

## Persona

**Alex**, age 30, software engineer.

| Parameter | Value |
|---|---|
| Current age | 30 |
| Retirement age | 45 |
| Planning horizon | to 90 |
| Monthly spending | $3,500 |
| Annual savings | $60,000 |
| Current portfolio | $350,000 |
| Allocation | 70/30 stocks/bonds |

```python
from monteplan.config.defaults import fire_plan
plan = fire_plan()
```

## Key Findings

### 1. The Base Case Is Challenging

With constant real spending and default market assumptions (7% stock returns, 3% bonds, 3% inflation), Alex's plan has moderate success. A 45-year retirement (age 45-90) is much longer than the traditional 30-year retirement the "4% rule" was designed for.

### 2. Spending Is the Biggest Lever

A parameter sweep over monthly spending shows a steep relationship:

- $2,500/mo: Significantly higher success
- $3,500/mo: Moderate success
- $4,500/mo: Low success

Even small spending reductions have outsized effects because they compound over 45 years.

### 3. Retirement Age Matters

Delaying retirement from 45 to 48 adds substantial safety margin through:

- 3 more years of contributions ($180K+)
- 3 more years of market growth
- 3 fewer years of withdrawals

### 4. Adaptive Spending Policies Help

For long retirements, guardrails and VPW spending policies outperform constant real spending. They automatically reduce withdrawals in bad markets, preventing the portfolio depletion spiral that kills long-horizon plans.

### 5. Sequence Risk Is the Key Threat

A market crash right before or at the start of retirement is the worst-case scenario. Alex should consider building a 1-2 year cash buffer before the retirement date.

## Takeaways

1. **Reduce spending first** -- it's the most powerful lever
2. **Consider guardrails spending** -- adaptive withdrawal rules handle 45-year horizons better
3. **Build flexibility** -- ability to adjust spending or work part-time provides a safety net
4. **Test with multiple return models** -- MVN, Student-t, and regime switching all tell different stories
5. **Stress test aggressively** -- a crash at age 44 is the scenario to plan for
