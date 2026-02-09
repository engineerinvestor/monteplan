"""Constant real spending policy."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.core.state import SimulationState


class ConstantRealSpending:
    """Spend a fixed real amount each month, adjusted for inflation.

    The nominal spending grows with cumulative inflation to maintain
    constant purchasing power.
    """

    def __init__(self, monthly_spending: float) -> None:
        self._base = monthly_spending

    def compute(self, state: SimulationState) -> NDArray[np.floating[Any]]:
        """Return inflation-adjusted monthly spending for each path."""
        result: NDArray[np.floating[Any]] = (
            np.full(state.n_paths, self._base) * state.cumulative_inflation
        )
        return result
