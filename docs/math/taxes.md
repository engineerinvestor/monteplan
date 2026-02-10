# Tax Model Mathematics

## US Federal Tax Model

### Ordinary Income Tax

Ordinary income (traditional account withdrawals, earned income) is taxed through progressive brackets after applying the standard deduction:

$$\text{taxable\_income} = \text{gross\_income} - \text{standard\_deduction}$$

Tax is computed by applying marginal rates to each bracket:

$$\text{tax} = \sum_{k=1}^{K} r_k \cdot \min(\max(\text{taxable\_income} - b_{k-1}, 0),\, b_k - b_{k-1})$$

where $r_k$ is the marginal rate for bracket $k$ and $[b_{k-1}, b_k)$ is the bracket range.

### 2024 Federal Tax Brackets (Single)

| Bracket | Rate |
|---|---|
| $0 -- $11,600 | 10% |
| $11,601 -- $47,150 | 12% |
| $47,151 -- $100,525 | 22% |
| $100,526 -- $191,950 | 24% |
| $191,951 -- $243,725 | 32% |
| $243,726 -- $609,350 | 35% |
| Over $609,350 | 37% |

Standard deduction (2024): $14,600 (single), $29,200 (married filing jointly).

### Long-Term Capital Gains

Taxable account gains are taxed at separate LTCG rates based on total income:

| Income Level (Single) | LTCG Rate |
|---|---|
| Up to $47,025 | 0% |
| $47,026 -- $518,900 | 15% |
| Over $518,900 | 20% |

### Vectorized Implementation

Tax calculations are vectorized across all simulation paths. The engine computes taxes for all paths simultaneously using numpy operations rather than per-path Python loops:

```python
compute_annual_tax_vectorized(
    ordinary_income: NDArray,    # (n_paths,)
    ltcg: NDArray,               # (n_paths,)
    filing_status: str,
) -> NDArray                     # (n_paths,)
```

## Required Minimum Distributions (RMDs)

Traditional account holders must take minimum distributions starting at age 73 (per current IRS rules). The RMD is calculated as:

$$\text{RMD} = \frac{\text{prior\_year\_balance}}{\text{divisor}(\text{age})}$$

### IRS Uniform Lifetime Table (Selected Values)

| Age | Divisor | Implied Rate |
|---|---|---|
| 73 | 26.5 | 3.8% |
| 75 | 24.6 | 4.1% |
| 80 | 20.2 | 5.0% |
| 85 | 16.0 | 6.3% |
| 90 | 12.2 | 8.2% |
| 95 | 8.6 | 11.6% |
| 100 | 6.4 | 15.6% |

The divisor table is loaded from `taxes/tables/rmd_divisors.yaml`.

## Flat Tax Model

The flat tax model applies a single effective rate to all taxable income:

$$\text{tax} = \text{rate} \times \text{gross\_income}$$

This is simpler but less realistic. It's useful for:

- Quick analysis where tax precision isn't critical
- Non-US users who want to model a different tax system
- Sensitivity analysis to isolate tax effects

## Withdrawal Tax Treatment

| Account Type | Tax Treatment |
|---|---|
| Taxable | Capital gains tax on appreciation only |
| Traditional (401k/IRA) | Ordinary income tax on full withdrawal |
| Roth | Tax-free |

### Tax Gross-Up

When withdrawing from a traditional account to meet spending needs, the engine applies a tax gross-up:

$$\text{gross\_withdrawal} = \frac{\text{needed\_spending}}{1 - \text{effective\_rate}}$$

This ensures the after-tax amount meets the spending target.
