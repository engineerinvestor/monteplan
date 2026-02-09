"""Multivariate normal return model."""

from __future__ import annotations

import numpy as np
from numpy.random import Generator

from monteplan.config.schema import MarketAssumptions


class MultivariateNormalReturns:
    """Generate correlated asset returns from a multivariate normal distribution.

    Converts annual return/volatility assumptions to monthly, then samples
    using the numpy multivariate normal generator.
    """

    def __init__(self, market: MarketAssumptions) -> None:
        annual_returns = np.array(market.expected_annual_returns)
        annual_vols = np.array(market.annual_volatilities)
        corr = np.array(market.correlation_matrix)

        # Convert annual to monthly: return/12, vol/sqrt(12)
        self._monthly_returns = annual_returns / 12.0
        monthly_vols = annual_vols / np.sqrt(12.0)

        # Build covariance matrix from correlation + monthly vols
        self._cov = np.outer(monthly_vols, monthly_vols) * corr

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate correlated monthly returns.

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        # Sample all paths and steps in one call, then reshape
        total_samples = n_paths * n_steps
        flat = rng.multivariate_normal(
            mean=self._monthly_returns,
            cov=self._cov,
            size=total_samples,
        )
        return flat.reshape(n_paths, n_steps, -1)
