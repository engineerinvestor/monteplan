# Return Model Mathematics

This page documents the mathematical formulation of each return model in monteplan.

## Annual-to-Monthly Conversion

All models convert annual assumptions to monthly:

$$\mu_{\text{monthly}} = \frac{\mu_{\text{annual}}}{12}$$

$$\sigma_{\text{monthly}} = \frac{\sigma_{\text{annual}}}{\sqrt{12}}$$

## Multivariate Normal (MVN)

Monthly returns are drawn from:

$$\mathbf{X}_t \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$$

where:

- $\boldsymbol{\mu}$ is the vector of monthly expected returns
- $\boldsymbol{\Sigma} = \text{diag}(\boldsymbol{\sigma}) \cdot \mathbf{C} \cdot \text{diag}(\boldsymbol{\sigma})$ is the covariance matrix
- $\mathbf{C}$ is the correlation matrix
- $\boldsymbol{\sigma}$ is the vector of monthly volatilities

In implementation, returns are generated using numpy's `multivariate_normal()` with the full covariance matrix.

## Student-t (Fat Tails)

Fat-tailed returns use the construction:

$$\mathbf{X}_t = \boldsymbol{\mu} + \boldsymbol{\sigma} \odot \frac{\mathbf{L} \mathbf{Z}_t}{\sqrt{W_t / \nu}}$$

where:

- $\mathbf{Z}_t \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ -- standard normal vector
- $W_t \sim \chi^2(\nu)$ -- chi-squared with $\nu$ degrees of freedom
- $\mathbf{L}$ is the Cholesky factor of the correlation matrix: $\mathbf{C} = \mathbf{L}\mathbf{L}^T$
- $\boldsymbol{\sigma}$ is the vector of monthly volatilities
- $\nu$ is the degrees of freedom parameter

The ratio $\sqrt{\nu / W_t}$ creates the heavy tails. When $\nu \to \infty$, this converges to the MVN model.

**Variance scaling:** The Student-t samples are scaled so that the marginal variance of each asset matches the specified volatility. For a Student-t distribution with $\nu$ degrees of freedom, the variance is $\nu / (\nu - 2)$, so the effective standard deviation is scaled by $\sqrt{(\nu-2)/\nu}$ to match the target volatility.

## Regime Switching (Markov)

The model defines $K$ discrete regimes (e.g., bull, normal, bear). At each time step:

1. **Regime selection:** The current regime $s_t$ determines which distribution parameters to use:

$$s_t \in \{1, 2, \ldots, K\}$$

2. **Return generation:** Conditioned on regime $s_t$, returns are drawn from a regime-specific MVN:

$$\mathbf{X}_t \mid s_t = k \sim \mathcal{N}(\boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k)$$

where each regime $k$ has its own means $\boldsymbol{\mu}_k$, volatilities $\boldsymbol{\sigma}_k$, and correlation matrix $\mathbf{C}_k$.

3. **Regime transition:** The next regime is drawn from a Markov chain:

$$P(s_{t+1} = j \mid s_t = i) = p_{ij}$$

The transition matrix $\mathbf{P} = [p_{ij}]$ is row-stochastic (rows sum to 1). Higher diagonal elements mean regimes are more persistent.

### Implementation

Regime transitions are vectorized across all paths using cumulative probability sums and `np.argmax`:

```
u ~ Uniform(0, 1)
next_regime = argmax(cumsum(P[current_regime, :]) > u)
```

Per-regime return generation uses boolean masking to select paths in each regime and apply the corresponding Cholesky factor.

## Historical Block Bootstrap

Returns are resampled from observed historical data in contiguous blocks:

1. Given historical data $\mathbf{H} \in \mathbb{R}^{T \times A}$ (T months, A assets)
2. Choose block size $b$ (default: 12 months)
3. For each path, randomly select starting indices and extract $b$-month blocks until $n_{\text{steps}}$ months are filled

The bootstrap preserves:

- **Cross-asset correlation** within each month (all assets come from the same historical month)
- **Serial autocorrelation** within blocks (contiguous sequences)
- **Non-normal features** of the historical distribution (skewness, kurtosis)

It cannot generate returns outside the range of observed history.

## Antithetic Variates

For variance reduction, the engine generates $n/2$ base draws and creates $n/2$ mirrored draws:

$$\mathbf{X}_t^{\text{anti}} = 2\boldsymbol{\mu} - \mathbf{X}_t^{\text{base}}$$

For Student-t, only the Z-scores are negated (the chi-squared scaling is kept the same).

For regime switching, the antithetic half uses the **same regime sequence** but **negated Z-scores**, ensuring both halves experience the same market regimes.

The antithetic estimator for any statistic $\theta$ is:

$$\hat{\theta}_{\text{anti}} = \frac{1}{2}\left(\hat{\theta}_{\text{base}} + \hat{\theta}_{\text{mirror}}\right)$$

This reduces variance when $\text{Cov}(\hat{\theta}_{\text{base}}, \hat{\theta}_{\text{mirror}}) < 0$, which holds for monotone functions of returns.
