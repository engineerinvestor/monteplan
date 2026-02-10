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
        max_start = self._n_months - self._block_size

        # Number of blocks needed to fill n_steps
        n_blocks = int(np.ceil(n_steps / self._block_size))

        # Generate all block start indices at once: (n_paths, n_blocks)
        block_starts = rng.integers(0, max_start + 1, size=(n_paths, n_blocks))

        # Build global indices: (n_paths, n_blocks, block_size)
        month_offsets = np.arange(self._block_size)
        global_idx = block_starts[:, :, np.newaxis] + month_offsets[np.newaxis, np.newaxis, :]

        # Gather all blocks via fancy indexing: (n_paths, n_blocks * block_size, n_assets)
        all_blocks = self._data[global_idx.reshape(n_paths, -1)]

        # Truncate to n_steps
        result: np.ndarray = all_blocks[:, :n_steps, :]
        return result
