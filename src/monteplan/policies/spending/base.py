"""Base protocol for spending policies."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from monteplan.core.state import SimulationState


class SpendingPolicy(Protocol):
    """Protocol for computing monthly spending amounts."""

    def compute(self, state: SimulationState) -> np.ndarray:
        """Compute monthly spending need for each path.

        Returns:
            Array of shape (n_paths,) with monthly spending amounts.
        """
        ...
