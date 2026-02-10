"""Guyton-Klinger guardrails spending policy."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.config.schema import GuardrailsConfig
from monteplan.core.state import SimulationState


class GuardrailsSpending:
    """Guyton-Klinger guardrails: adjust spending based on withdrawal rate.

    Decision rules:
    - Start with initial_withdrawal_rate * portfolio value.
    - **Prosperity rule:** if current withdrawal rate drops below
      initial_rate * (1 - upper_threshold), raise spending by raise_pct.
    - **Capital preservation rule:** if current withdrawal rate exceeds
      initial_rate * (1 + lower_threshold), cut spending by cut_pct.
    """

    def __init__(self, config: GuardrailsConfig) -> None:
        self._initial_rate = config.initial_withdrawal_rate
        self._upper_threshold = config.upper_threshold
        self._lower_threshold = config.lower_threshold
        self._raise_pct = config.raise_pct
        self._cut_pct = config.cut_pct

    def compute(self, state: SimulationState) -> NDArray[np.floating[Any]]:
        """Compute monthly spending with guardrails adjustments."""
        wealth = state.total_wealth
        current_spending = state.current_spending.copy()

        # On first call (no spending set), initialize
        needs_init = current_spending <= 0
        if needs_init.any():
            # Use initial portfolio value if set, otherwise current wealth
            init_val = np.where(
                state.initial_portfolio_value > 0,
                state.initial_portfolio_value,
                wealth,
            )
            current_spending = np.where(
                needs_init,
                init_val * self._initial_rate / 12.0,
                current_spending,
            )

        # Current annual withdrawal rate = (monthly_spending * 12) / wealth
        safe_wealth = np.where(wealth > 0, wealth, 1.0)
        current_annual_rate = (current_spending * 12.0) / safe_wealth

        # Prosperity rule: rate too low → raise spending
        prosperity_threshold = self._initial_rate * (1.0 - self._upper_threshold)
        raise_mask = current_annual_rate < prosperity_threshold
        current_spending = np.where(
            raise_mask & (wealth > 0),
            current_spending * (1.0 + self._raise_pct),
            current_spending,
        )

        # Capital preservation rule: rate too high → cut spending
        preservation_threshold = self._initial_rate * (1.0 + self._lower_threshold)
        cut_mask = current_annual_rate > preservation_threshold
        current_spending = np.where(
            cut_mask & (wealth > 0),
            current_spending * (1.0 - self._cut_pct),
            current_spending,
        )

        # Apply inflation adjustment (via cumulative_inflation)
        # Guardrails spending is already in nominal terms; adjust base
        current_spending = np.where(wealth > 0, current_spending, 0.0)

        # Update state for next step
        state.current_spending = current_spending

        result: NDArray[np.floating[Any]] = current_spending
        return result
