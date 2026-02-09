"""Mutable simulation state passed through each time step."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class SimulationState:
    """Mutable state for all paths at a given time step.

    Uses plain numpy arrays for performance. NOT Pydantic — this is mutated
    every step in the hot loop.

    Attributes:
        balances: (n_paths, n_accounts) account balances.
        cumulative_inflation: (n_paths,) cumulative inflation factor (starts at 1.0).
        is_depleted: (n_paths,) boolean mask for paths with zero total wealth.
        step: Current time step index.
        n_paths: Number of simulation paths.
        n_accounts: Number of accounts.
        account_types: List of account type strings.
    """

    balances: NDArray[np.floating[Any]]
    cumulative_inflation: NDArray[np.floating[Any]]
    is_depleted: NDArray[np.bool_]
    step: int
    n_paths: int
    n_accounts: int
    account_types: list[str] = field(default_factory=list)

    @classmethod
    def initialize(
        cls,
        n_paths: int,
        initial_balances: list[float],
        account_types: list[str],
    ) -> SimulationState:
        """Create initial simulation state."""
        n_accounts = len(initial_balances)
        balances = np.tile(initial_balances, (n_paths, 1))
        return cls(
            balances=balances,
            cumulative_inflation=np.ones(n_paths),
            is_depleted=np.zeros(n_paths, dtype=bool),
            step=0,
            n_paths=n_paths,
            n_accounts=n_accounts,
            account_types=account_types,
        )

    @property
    def total_wealth(self) -> NDArray[np.floating[Any]]:
        """Total wealth across all accounts, shape (n_paths,)."""
        result: NDArray[np.floating[Any]] = self.balances.sum(axis=1)
        return result
