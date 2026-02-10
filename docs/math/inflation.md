# Inflation Model Mathematics

## Ornstein-Uhlenbeck Process

Inflation in monteplan follows a mean-reverting Ornstein-Uhlenbeck (OU) process:

$$dI_t = \kappa(\theta - I_t)\,dt + \sigma\,dW_t$$

where:

| Parameter | Symbol | Default | Description |
|---|---|---|---|
| Long-run mean | $\theta$ | 0.03 | Target annualized inflation rate |
| Mean-reversion speed | $\kappa$ | 0.5 | How quickly inflation reverts to $\theta$ |
| Volatility | $\sigma$ | 0.01 | Annual standard deviation of inflation shocks |
| Wiener process | $dW_t$ | -- | Standard Brownian motion increment |

## Discretization

The OU SDE is discretized with an Euler-Maruyama scheme at monthly time steps ($\Delta t = 1/12$):

$$I_{t+1} = I_t + \kappa(\theta - I_t)\Delta t + \sigma\sqrt{\Delta t}\,\epsilon_t$$

where $\epsilon_t \sim \mathcal{N}(0, 1)$.

The annualized rate $I_t$ is converted to a monthly rate by dividing by 12:

$$i_t^{\text{monthly}} = \frac{I_t}{12}$$

## Initialization

All paths start at $I_0 = \theta$ (the long-run mean).

## Properties

The OU process has the following stationary properties:

- **Stationary mean:** $E[I_\infty] = \theta$
- **Stationary variance:** $\text{Var}(I_\infty) = \frac{\sigma^2}{2\kappa}$
- **Half-life:** $t_{1/2} = \frac{\ln 2}{\kappa}$

With the default parameters ($\kappa = 0.5$, $\sigma = 0.01$):

- Stationary standard deviation: $\sqrt{0.01^2 / (2 \times 0.5)} = 1.0\%$
- Half-life: $\ln 2 / 0.5 \approx 1.4$ years

## Regime-Coupled Inflation

When using the regime-switching return model, inflation parameters become regime-dependent:

$$dI_t = \kappa(\theta_{s_t} - I_t)\,dt + \sigma_{s_t}\,dW_t$$

where $s_t$ is the current market regime. Each regime provides its own:

- $\theta_k$ -- long-run inflation target
- $\sigma_k$ -- inflation volatility

This couples inflation dynamics to market conditions. For example, a "bear" regime might have higher inflation targets and volatility than a "bull" regime.

The regime indices are shared with the return model -- the same regime sequence drives both returns and inflation.

## Cumulative Inflation

The engine tracks cumulative inflation as a multiplicative factor:

$$\text{CPI}_t = \prod_{s=0}^{t-1}(1 + i_s^{\text{monthly}})$$

This factor is used to adjust:

- Retirement spending (constant real spending policy)
- Floor and ceiling bounds
- Guaranteed income streams with COLA

## Antithetic Inflation

When antithetic variates are enabled, inflation uses the same approach as returns:

- Generate $n/2$ base noise draws $\epsilon_t$
- Mirror them as $-\epsilon_t$ for the antithetic half
- Both halves start at the same $I_0 = \theta$

This ensures the antithetic inflation paths are negatively correlated with the base paths, reducing variance in the final estimates.
