"""Markov regime-switching return model."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.random import Generator
from numpy.typing import NDArray

from monteplan.config.schema import RegimeSwitchingConfig


class RegimeSwitchingReturns:
    """Generate correlated asset returns with Markov regime switching.

    Each regime has its own mean returns, volatilities, and correlation
    structure. Regime transitions follow a discrete Markov chain with
    a pre-specified transition matrix.
    """

    def __init__(self, config: RegimeSwitchingConfig, antithetic: bool = False) -> None:
        self._config = config
        self._n_regimes = len(config.regimes)
        n_assets = len(config.regimes[0].expected_annual_returns)
        self._n_assets = n_assets
        self._initial_regime = config.initial_regime
        self._antithetic = antithetic

        # Pre-compute per-regime monthly means, Cholesky factors
        self._monthly_means: list[NDArray[np.floating[Any]]] = []
        self._chol_factors: list[NDArray[np.floating[Any]]] = []
        self._monthly_vols: list[NDArray[np.floating[Any]]] = []

        for regime in config.regimes:
            annual_returns = np.array(regime.expected_annual_returns)
            annual_vols = np.array(regime.annual_volatilities)
            corr = np.array(regime.correlation_matrix)

            monthly_means = annual_returns / 12.0
            monthly_vols = annual_vols / np.sqrt(12.0)

            self._monthly_means.append(monthly_means)
            self._monthly_vols.append(monthly_vols)
            self._chol_factors.append(np.linalg.cholesky(corr))

        # Cumulative transition probabilities for searchsorted
        trans = np.array(config.transition_matrix)
        self._cum_trans = np.cumsum(trans, axis=1)

        # Stored after sampling for inflation model coupling
        self.regime_indices: NDArray[np.intp] | None = None

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> NDArray[np.floating[Any]]:
        """Generate correlated monthly returns with regime switching.

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        half = n_paths // 2 if self._antithetic else n_paths

        returns = np.empty((half, n_steps, self._n_assets))
        regime_indices = np.empty((half, n_steps), dtype=np.intp)

        # Initialize regimes
        regimes = np.full(half, self._initial_regime, dtype=np.intp)

        # Store Z draws for antithetic mirroring
        all_z = np.empty((n_steps, half, self._n_assets)) if self._antithetic else None

        for t in range(n_steps):
            regime_indices[:, t] = regimes

            # Pre-generate standard normals for base paths
            z = rng.standard_normal((half, self._n_assets))
            if all_z is not None:
                all_z[t] = z

            # Process each regime: select paths, apply regime-specific params
            for r in range(self._n_regimes):
                mask = regimes == r
                if not mask.any():
                    continue
                # Correlate via Cholesky
                correlated = z[mask] @ self._chol_factors[r].T
                # Scale by monthly vols and add means
                returns[mask, t, :] = self._monthly_means[r] + self._monthly_vols[r] * correlated

            # Transition regimes for next step (vectorized)
            u = rng.random(half)
            cum_probs = self._cum_trans[regimes]  # (half, n_regimes)
            # Find first column where cumulative probability exceeds uniform draw
            regimes = np.argmax(cum_probs > u[:, np.newaxis], axis=1).astype(np.intp)
            np.clip(regimes, 0, self._n_regimes - 1, out=regimes)

        if self._antithetic:
            assert all_z is not None
            # Build antithetic paths: same regime sequence, negated Z draws
            anti_returns = np.empty((half, n_steps, self._n_assets))
            for t in range(n_steps):
                neg_z = -all_z[t]
                regimes_t = regime_indices[:, t]
                for r in range(self._n_regimes):
                    mask = regimes_t == r
                    if not mask.any():
                        continue
                    correlated = neg_z[mask] @ self._chol_factors[r].T
                    anti_returns[mask, t, :] = (
                        self._monthly_means[r] + self._monthly_vols[r] * correlated
                    )

            # Concatenate: base + antithetic, regime indices duplicated
            full_returns: NDArray[np.floating[Any]] = np.concatenate(
                [returns, anti_returns], axis=0
            )
            self.regime_indices = np.concatenate([regime_indices, regime_indices], axis=0)
            return full_returns
        else:
            self.regime_indices = regime_indices
            result: NDArray[np.floating[Any]] = returns
            return result
