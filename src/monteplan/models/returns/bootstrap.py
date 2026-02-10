"""Historical block bootstrap return model."""

from __future__ import annotations

import numpy as np
from numpy.random import Generator


class HistoricalBootstrapReturns:
    """Block bootstrap from historical monthly returns.

    Samples contiguous blocks of historical returns to preserve
    autocorrelation structure, then tiles to fill the required
    number of steps.
    """

    def __init__(
        self,
        historical_returns: np.ndarray,
        block_size: int = 12,
    ) -> None:
        """Initialize with historical data.

        Args:
            historical_returns: (n_months, n_assets) array of historical monthly returns.
            block_size: Number of contiguous months per block.
        """
        self._data = np.asarray(historical_returns)
        self._block_size = block_size
        self._n_months, self._n_assets = self._data.shape

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate bootstrapped monthly returns.

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        result = np.empty((n_paths, n_steps, self._n_assets))
        max_start = self._n_months - self._block_size

        # Number of blocks needed to fill n_steps
        n_blocks = int(np.ceil(n_steps / self._block_size))

        for p in range(n_paths):
            blocks = []
            for _ in range(n_blocks):
                # Random block start index
                start = rng.integers(0, max_start + 1)
                blocks.append(self._data[start : start + self._block_size])
            # Concatenate and truncate to n_steps
            path = np.concatenate(blocks, axis=0)[:n_steps]
            result[p] = path

        return result
