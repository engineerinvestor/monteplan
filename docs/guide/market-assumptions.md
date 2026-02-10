# Market Assumptions

`MarketAssumptions` defines the asset universe, expected returns, volatilities, correlations, and inflation model.

## Basic Setup

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

## Assets and Allocation

Each `AssetClass` has a `name` and a `weight` (target allocation). Weights must sum to 1.0:

```python
assets = [
    AssetClass(name="US Stocks", weight=0.6),
    AssetClass(name="Intl Stocks", weight=0.2),
    AssetClass(name="US Bonds", weight=0.2),
]
```

The `expected_annual_returns`, `annual_volatilities`, and `correlation_matrix` arrays must have the same number of elements as `assets`.

## Correlation Matrix

The correlation matrix controls co-movement between assets. It must be:

- Square (n_assets x n_assets)
- Symmetric
- Have 1.0 on the diagonal

Example for 3 assets:

```python
correlation_matrix = [
    [1.0,  0.3, -0.1],
    [0.3,  1.0,  0.2],
    [-0.1, 0.2,  1.0],
]
```

## Return Model Selection

Choose how returns are generated with `return_model`:

| Model | Value | Best For |
|---|---|---|
| Multivariate Normal | `"mvn"` (default) | Standard analysis, quick runs |
| Student-t | `"student_t"` | Fat-tailed scenarios |
| Block Bootstrap | `"bootstrap"` | When you have historical data |
| Regime Switching | `"regime_switching"` | Bull/bear market dynamics |

```python
# Fat-tailed returns
market = MarketAssumptions(
    ...,
    return_model="student_t",
    degrees_of_freedom=5.0,
)
```

See [Return Models](return-models.md) for detailed guidance on each model.

## Inflation

Inflation follows an Ornstein-Uhlenbeck mean-reverting process:

| Field | Default | Description |
|---|---|---|
| `inflation_mean` | 0.03 | Long-run annual inflation rate |
| `inflation_vol` | 0.01 | Annual inflation volatility |

See [Inflation Math](../math/inflation.md) for the underlying model.

## Glide Paths

Shift asset allocation over time (e.g., more bonds as you age):

```python
from monteplan.config.schema import GlidePath

market = MarketAssumptions(
    ...,
    glide_path=GlidePath(
        start_age=30,
        start_weights=[0.9, 0.1],    # 90/10 stocks/bonds at age 30
        end_age=70,
        end_weights=[0.4, 0.6],      # 40/60 stocks/bonds at age 70
    ),
)
```

The engine linearly interpolates weights between `start_age` and `end_age`. Beyond `end_age`, the `end_weights` are held constant.

## Investment Fees

Three fee types, applied as monthly drag on portfolio value:

| Field | Default | Description |
|---|---|---|
| `expense_ratio` | 0.0 | Annual fund expense ratio (e.g., 0.001 = 10 bps) |
| `aum_fee` | 0.0 | Annual AUM/platform fee |
| `advisory_fee` | 0.0 | Annual financial advisor fee |

```python
market = MarketAssumptions(
    ...,
    expense_ratio=0.001,    # 10 bps fund expenses
    advisory_fee=0.01,      # 1% advisor fee
)
```

The total annual fee drag is `expense_ratio + aum_fee + advisory_fee`, applied monthly as `(1 - annual_fee / 12)` on positions.
