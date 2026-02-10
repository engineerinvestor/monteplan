"""Ornstein-Uhlenbeck mean-reverting inflation model."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray

from monteplan.config.schema import RegimeConfig


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
        antithetic: bool = False,
    ) -> None:
        self._theta = theta
        self._sigma = sigma
        self._kappa = kappa
        self._dt = 1.0 / 12.0  # monthly time step
        self._antithetic = antithetic

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate monthly inflation rate paths.

        Returns:
            Array of shape (n_paths, n_steps) with monthly inflation rates
            (i.e., annual rate / 12 per step).
        """
        if self._antithetic:
            half = n_paths // 2
            rates_base = np.empty((half, n_steps))
            rates_anti = np.empty((half, n_steps))
            current_base = np.full(half, self._theta)
            current_anti = np.full(half, self._theta)

            for t in range(n_steps):
                noise = rng.standard_normal(half)
                current_base = (
                    current_base
                    + self._kappa * (self._theta - current_base) * self._dt
                    + self._sigma * np.sqrt(self._dt) * noise
                )
                current_anti = (
                    current_anti
                    + self._kappa * (self._theta - current_anti) * self._dt
                    + self._sigma * np.sqrt(self._dt) * (-noise)
                )
                rates_base[:, t] = current_base / 12.0
                rates_anti[:, t] = current_anti / 12.0

            return np.concatenate([rates_base, rates_anti], axis=0)
        else:
            rates = np.empty((n_paths, n_steps))
            current = np.full(n_paths, self._theta)

            for t in range(n_steps):
                noise = rng.standard_normal(n_paths)
                current = (
                    current
                    + self._kappa * (self._theta - current) * self._dt
                    + self._sigma * np.sqrt(self._dt) * noise
                )
                rates[:, t] = current / 12.0

            return rates


class RegimeSwitchingInflationModel:
    """OU inflation with regime-dependent theta/sigma.

    At each time step, the mean-reversion target (theta) and volatility
    (sigma) are determined by the current market regime, coupling inflation
    dynamics to the regime-switching return model.
    """

    def __init__(
        self,
        regimes: list[RegimeConfig],
        kappa: float = 0.5,
    ) -> None:
        self._kappa = kappa
        self._dt = 1.0 / 12.0
        # Per-regime parameters
        self._thetas = np.array([r.inflation_mean for r in regimes])
        self._sigmas = np.array([r.inflation_vol for r in regimes])

    def sample(
        self,
        n_paths: int,
        n_steps: int,
        rng: Generator,
        regime_indices: NDArray[np.intp],
    ) -> NDArray[np.floating[Any]]:
        """Generate monthly inflation rate paths with regime-dependent parameters.

        Args:
            n_paths: Number of simulation paths.
            n_steps: Number of monthly time steps.
            rng: Numpy random generator.
            regime_indices: (n_paths, n_steps) array of regime indices from
                the regime-switching return model.

        Returns:
            Array of shape (n_paths, n_steps) with monthly inflation rates.
        """
        rates = np.empty((n_paths, n_steps))
        # Start at the mean of the initial regime
        initial_regimes = regime_indices[:, 0]
        current = self._thetas[initial_regimes].copy()

        for t in range(n_steps):
            # Look up regime-dependent theta and sigma
            regimes_t = regime_indices[:, t]
            theta_t = self._thetas[regimes_t]
            sigma_t = self._sigmas[regimes_t]

            noise = rng.standard_normal(n_paths)
            current = (
                current
                + self._kappa * (theta_t - current) * self._dt
                + sigma_t * np.sqrt(self._dt) * noise
            )
            rates[:, t] = current / 12.0

        result: NDArray[np.floating[Any]] = rates
        return result
