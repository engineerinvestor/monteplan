"""Variable Percentage Withdrawal (VPW) spending policy."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.config.schema import VPWConfig
from monteplan.core.state import SimulationState


class VPWSpending:
    """Variable Percentage Withdrawal: rate varies by remaining years.

    Withdrawal rate = 1 / remaining_years, bounded by min_rate and max_rate.
    Monthly spending = (rate / 12) * total_wealth.
    """

    def __init__(self, config: VPWConfig, end_age: int, current_age: int) -> None:
        self._min_rate = config.min_rate
        self._max_rate = config.max_rate
        self._end_age = end_age
        self._current_age = current_age

    def compute(self, state: SimulationState) -> NDArray[np.floating[Any]]:
        """Compute monthly spending based on remaining life expectancy."""
        age = self._current_age + state.step / 12.0
        remaining_years = max(self._end_age - age, 1.0)

        # Rate = 1 / remaining_years, bounded
        rate = 1.0 / remaining_years
        rate = max(self._min_rate, min(rate, self._max_rate))

        monthly_rate = rate / 12.0
        result: NDArray[np.floating[Any]] = monthly_rate * np.maximum(state.total_wealth, 0.0)
        return result
