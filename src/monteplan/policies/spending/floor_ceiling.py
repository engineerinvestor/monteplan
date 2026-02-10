"""Floor-and-ceiling spending policy."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.config.schema import FloorCeilingConfig
from monteplan.core.state import SimulationState


class FloorCeilingSpending:
    """Spend a percentage of portfolio, clamped between a floor and ceiling.

    Monthly spending = clamp(rate/12 * wealth, floor * inflation, ceiling * inflation).
    Floor and ceiling are specified in today's dollars and grow with inflation.
    """

    def __init__(self, config: FloorCeilingConfig) -> None:
        self._monthly_rate = config.withdrawal_rate / 12.0
        self._floor = config.floor
        self._ceiling = config.ceiling

    def compute(self, state: SimulationState) -> NDArray[np.floating[Any]]:
        """Return clamped monthly spending for each path."""
        base_spending = self._monthly_rate * np.maximum(state.total_wealth, 0.0)
        floor_nominal = self._floor * state.cumulative_inflation
        ceiling_nominal = self._ceiling * state.cumulative_inflation
        result: NDArray[np.floating[Any]] = np.clip(base_spending, floor_nominal, ceiling_nominal)
        return result
