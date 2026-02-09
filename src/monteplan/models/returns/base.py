"""Base protocol for return models."""

from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.random import Generator


class ReturnModel(Protocol):
    """Protocol for asset return generators."""

    def sample(self, n_paths: int, n_steps: int, rng: Generator) -> np.ndarray:
        """Generate random returns.

        Returns:
            Array of shape (n_paths, n_steps, n_assets) with monthly returns.
        """
        ...
