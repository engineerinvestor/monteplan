"""Percent-of-portfolio spending policy."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.core.state import SimulationState


class PercentOfPortfolioSpending:
    """Spend a fixed percentage of total portfolio value each month.

    Monthly spending = (annual_rate / 12) * total_wealth.
    Returns zero when wealth is zero.
    """

    def __init__(self, annual_rate: float) -> None:
        self._monthly_rate = annual_rate / 12.0

    def compute(self, state: SimulationState) -> NDArray[np.floating[Any]]:
        """Return percentage-based monthly spending for each path."""
        result: NDArray[np.floating[Any]] = self._monthly_rate * np.maximum(
            state.total_wealth, 0.0
        )
        return result
