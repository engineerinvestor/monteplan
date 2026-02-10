# Case Study: Conservative Retiree

!!! info "Interactive Version"
    Run this case study yourself: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/engineerinvestor/monteplan/blob/main/notebooks/05_case_study_retiree.ipynb)

## Persona

**Pat**, age 60, nearing traditional retirement.

| Parameter | Value |
|---|---|
| Current age | 60 |
| Retirement age | 65 |
| Planning horizon | to 95 |
| Monthly spending | $5,000 |
| Current portfolio | $700,000 |
| Social Security | $2,500/mo at age 67, 2% COLA |
| Allocation | 70/30 stocks/bonds |

```python
from monteplan.config.defaults import conservative_retiree_plan
plan = conservative_retiree_plan()
```

## Key Findings

### 1. Social Security Is Transformative

The single biggest factor in Pat's plan is the $2,500/month Social Security benefit. It covers half of the spending need, reducing the portfolio withdrawal rate dramatically. Comparing with and without Social Security shows a large difference in success probability.

### 2. Glide Path Considerations

Pat can shift from 70/30 to a more conservative allocation over time:

| Strategy | Description |
|---|---|
| Static 70/30 | Maintain allocation throughout |
| Glide to 40/60 | Shift to 40% stocks by age 80 |
| Glide to 30/70 | Shift to 30% stocks by age 80 |

The more aggressive allocation generally provides higher expected outcomes but wider uncertainty bands. For Pat, with Social Security as a floor, maintaining some equity exposure may be appropriate.

### 3. Tax Model Matters

Pat's portfolio is heavily weighted toward a traditional 401k ($500K of $700K). With the US federal progressive tax model, withdrawals push income through progressively higher brackets. The difference between flat and progressive tax models can be meaningful.

### 4. Inflation Is the Key Risk

For a 30-year retirement, inflation is the dominant risk factor:

- At 2% average inflation, the plan has strong success
- At 4% average inflation, success drops significantly
- The 2% COLA on Social Security offsets about two-thirds of the default 3% inflation assumption

## Strategies for Pat

### Conservative Approach
- Glide to 40/60 by age 80
- Use guardrails spending to adapt to market conditions
- Delay Social Security to 70 if possible (benefit increases ~8%/year from 67 to 70)

### Moderate Approach
- Maintain 60/40 allocation
- Use constant real spending at $4,500/month (slightly below desire)
- Claim Social Security at 67

### Aggressive Approach
- Maintain 70/30 allocation
- Spend $5,000/month as planned
- Accept higher variance in outcomes for higher expected wealth

## Takeaways

1. **Social Security is the foundation** -- it provides inflation-adjusted guaranteed income that dramatically reduces portfolio risk
2. **Tax-aware withdrawal ordering matters** -- draw from taxable first, traditional second, Roth last
3. **Inflation is the primary threat** -- consider TIPS or I-bonds as a partial hedge
4. **Glide paths provide peace of mind** but may reduce expected outcomes
5. **The plan is more robust than FIRE plans** -- shorter retirement + guaranteed income = higher success rates
