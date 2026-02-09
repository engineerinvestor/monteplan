"""Ornstein-Uhlenbeck mean-reverting inflation model."""

from __future__ import annotations

import numpy as np
from numpy.random import Generator


class OUInflationModel:
    """Stochastic inflation via an Ornstein-Uhlenbeck process.

    dI = kappa * (theta - I) * dt + sigma * dW

    where:
        I = annualized inflation rate
        theta = long-run mean inflation
        kappa = mean-reversion speed
        sigma = annual volatility of inflation
    """

    def __init__(
        self,
        theta: float = 0.03,
        sigma: float = 0.01,
        kappa: float = 0.5,
    ) -> None:
        self._theta = theta
        self._sigma = sigma
        self._kappa = kappa
        self._dt = 1.0 / 12.0  # monthly time step

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate monthly inflation rate paths.

        Returns:
            Array of shape (n_paths, n_steps) with monthly inflation rates
            (i.e., annual rate / 12 per step).
        """
        rates = np.empty((n_paths, n_steps))
        # Start at the long-run mean
        current = np.full(n_paths, self._theta)

        for t in range(n_steps):
            # OU discrete step
            noise = rng.standard_normal(n_paths)
            current = (
                current
                + self._kappa * (self._theta - current) * self._dt
                + self._sigma * np.sqrt(self._dt) * noise
            )
            # Store as monthly rate
            rates[:, t] = current / 12.0

        return rates
