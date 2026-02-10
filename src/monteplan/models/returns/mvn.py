"""Multivariate normal and student-t return models."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray

from monteplan.config.schema import MarketAssumptions


class MultivariateNormalReturns:
    """Generate correlated asset returns from a multivariate normal distribution.

    Converts annual return/volatility assumptions to monthly, then samples
    using the numpy multivariate normal generator.
    """

    def __init__(self, market: MarketAssumptions, antithetic: bool = False) -> None:
        annual_returns = np.array(market.expected_annual_returns)
        annual_vols = np.array(market.annual_volatilities)
        corr = np.array(market.correlation_matrix)

        # Convert annual to monthly: return/12, vol/sqrt(12)
        self._monthly_returns = annual_returns / 12.0
        monthly_vols = annual_vols / np.sqrt(12.0)

        # Build covariance matrix from correlation + monthly vols
        self._cov = np.outer(monthly_vols, monthly_vols) * corr
        self._antithetic = antithetic

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate correlated monthly returns.

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        if self._antithetic:
            half = n_paths // 2
            total_samples = half * n_steps
            flat = rng.multivariate_normal(
                mean=self._monthly_returns,
                cov=self._cov,
                size=total_samples,
            )
            base = flat.reshape(half, n_steps, -1)
            # Antithetic: reflect around mean (negate deviation from mean)
            anti = 2.0 * self._monthly_returns - flat
            anti = anti.reshape(half, n_steps, -1)
            return np.concatenate([base, anti], axis=0)
        else:
            total_samples = n_paths * n_steps
            flat = rng.multivariate_normal(
                mean=self._monthly_returns,
                cov=self._cov,
                size=total_samples,
            )
            return flat.reshape(n_paths, n_steps, -1)


class StudentTReturns:
    """Generate correlated asset returns from a multivariate student-t distribution.

    Uses Cholesky decomposition + univariate t-distributed marginals
    to produce correlated fat-tailed returns.
    """

    def __init__(self, market: MarketAssumptions, antithetic: bool = False) -> None:
        annual_returns = np.array(market.expected_annual_returns)
        annual_vols = np.array(market.annual_volatilities)
        corr = np.array(market.correlation_matrix)

        self._monthly_returns = annual_returns / 12.0
        monthly_vols = annual_vols / np.sqrt(12.0)

        # Cholesky factor of correlation matrix
        self._chol = np.linalg.cholesky(corr)
        self._monthly_vols = monthly_vols
        self._n_assets = len(annual_returns)
        self._antithetic = antithetic

        if market.degrees_of_freedom is None:
            raise ValueError("degrees_of_freedom must be set for student-t model")
        self._df = market.degrees_of_freedom

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate correlated fat-tailed monthly returns.

        Uses the approach: X = mu + sigma * L @ (Z / sqrt(W/df))
        where Z ~ N(0,1) and W ~ chi2(df), L = cholesky(corr).

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        if self._antithetic:
            half = n_paths // 2
            total = half * n_steps
        else:
            half = n_paths
            total = n_paths * n_steps

        # Independent standard normals
        z = rng.standard_normal((total, self._n_assets))  # (total, n_assets)

        # Correlate via Cholesky
        correlated = z @ self._chol.T  # (total, n_assets)

        # Chi-squared for t-distribution scaling
        chi2 = rng.chisquare(self._df, size=total)  # (total,)
        scaling = np.sqrt(self._df / chi2)  # (total,)

        # Apply t-distribution scaling
        t_samples = correlated * scaling[:, np.newaxis]  # (total, n_assets)

        # Scale by monthly vols and add means
        base = self._monthly_returns + self._monthly_vols * t_samples

        if self._antithetic:
            base_shaped = base.reshape(half, n_steps, self._n_assets)
            # Negate the Z draws (keep same chi2 scaling)
            anti_t = -correlated * scaling[:, np.newaxis]
            anti = self._monthly_returns + self._monthly_vols * anti_t
            anti_shaped = anti.reshape(half, n_steps, self._n_assets)
            result: NDArray[np.floating[Any]] = np.concatenate([base_shaped, anti_shaped], axis=0)
            return result
        else:
            shaped: NDArray[np.floating[Any]] = base.reshape(n_paths, n_steps, self._n_assets)
            return shaped
