# Return Models

monteplan supports four return models, each suited to different analysis goals. All implement the `ReturnModel` protocol and generate a 3D array of shape `(n_paths, n_steps, n_assets)`.

## Multivariate Normal (MVN)

The default model. Returns are drawn from a multivariate normal distribution with the specified means, volatilities, and correlation structure.

**When to use:** Standard analysis, quick prototyping, sensitivity studies.

```python
market = MarketAssumptions(
    ...,
    return_model="mvn",  # default
)
```

**Characteristics:**

- Symmetric return distributions (no skew)
- Light tails (extreme events are rare)
- Analytically tractable
- Fastest to generate

## Student-t (Fat Tails)

Returns are drawn from a multivariate Student-t distribution with user-specified degrees of freedom. Lower degrees of freedom = heavier tails = more extreme events.

**When to use:** Stress-testing for tail risk, realistic crash modeling.

```python
market = MarketAssumptions(
    ...,
    return_model="student_t",
    degrees_of_freedom=5.0,  # heavier tails than normal
)
```

**Degrees of freedom guidance:**

| df | Tail Behavior |
|---|---|
| > 30 | Nearly identical to MVN |
| 10 | Slightly heavier tails |
| 5 | Noticeably heavier tails (recommended) |
| 3 | Very heavy tails (extreme events frequent) |

## Historical Block Bootstrap

Resamples returns from actual historical data in contiguous blocks, preserving serial correlation and cross-asset correlation.

**When to use:** When you have historical return data and want to avoid parametric assumptions.

```python
# historical_returns: list of [n_months] lists, each with [n_assets] values
market = MarketAssumptions(
    ...,
    return_model="bootstrap",
    historical_returns=historical_data,  # (n_months, n_assets) as nested lists
    bootstrap_block_size=12,              # 12-month blocks
)
```

**Characteristics:**

- Non-parametric: no distributional assumptions
- Preserves autocorrelation within blocks
- Limited to the range of observed history (cannot generate worse-than-observed crashes)
- Block size controls the tradeoff between preserving serial correlation and sample diversity

## Regime Switching (Markov)

A Markov model with 2-5 discrete market regimes (e.g., bull, bear, normal). Each regime has its own return distribution, volatility, and inflation parameters. Transitions between regimes follow a row-stochastic transition matrix.

**When to use:** Modeling persistent market conditions, bull/bear cycles, structurally different environments.

```python
from monteplan.config.schema import RegimeSwitchingConfig, RegimeConfig

market = MarketAssumptions(
    ...,
    return_model="regime_switching",
    regime_switching=RegimeSwitchingConfig(
        regimes=[
            RegimeConfig(
                name="bull",
                expected_annual_returns=[0.12, 0.05],
                annual_volatilities=[0.12, 0.04],
                correlation_matrix=[[1.0, -0.1], [-0.1, 1.0]],
                inflation_mean=0.025,
                inflation_vol=0.008,
            ),
            RegimeConfig(
                name="normal",
                expected_annual_returns=[0.07, 0.03],
                annual_volatilities=[0.16, 0.06],
                correlation_matrix=[[1.0, 0.0], [0.0, 1.0]],
                inflation_mean=0.03,
                inflation_vol=0.01,
            ),
            RegimeConfig(
                name="bear",
                expected_annual_returns=[-0.05, 0.01],
                annual_volatilities=[0.25, 0.08],
                correlation_matrix=[[1.0, 0.3], [0.3, 1.0]],
                inflation_mean=0.04,
                inflation_vol=0.02,
            ),
        ],
        transition_matrix=[
            [0.95, 0.04, 0.01],
            [0.05, 0.90, 0.05],
            [0.05, 0.10, 0.85],
        ],
        initial_regime=1,  # start in "normal"
    ),
)
```

**Transition matrix:** Row `i` gives the probability of transitioning from regime `i` to each other regime. Rows must sum to 1.0. Higher diagonal values mean regimes are more persistent.

**Coupled inflation:** When using regime switching, inflation parameters come from the active regime rather than the top-level `inflation_mean` / `inflation_vol`.

## Antithetic Variates

All return models support antithetic variates for variance reduction. When enabled, the engine generates `n_paths / 2` draws and mirrors them (negates the Z-scores) to produce the other half. This reduces variance in success probability estimates without doubling compute time.

```python
from monteplan.config.schema import SimulationConfig

sim_config = SimulationConfig(
    n_paths=5000,   # must be even when antithetic=True
    antithetic=True,
)
```

## Choosing a Model

| Consideration | MVN | Student-t | Bootstrap | Regime |
|---|---|---|---|---|
| Speed | Fastest | Fast | Fast | Moderate |
| Tail risk | Light | Heavy | Historical | Per-regime |
| Serial correlation | None | None | Preserved | Via regimes |
| Setup complexity | Low | Low | Need data | Moderate |
| Best for | Prototyping | Stress tests | Data-driven | Cycle analysis |

See the [mathematical details](../math/return-models.md) for formulas and implementation notes.
