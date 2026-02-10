"""Required Minimum Distribution (RMD) computation."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from monteplan.io.yaml_loader import load_package_yaml


class RMDCalculator:
    """Compute Required Minimum Distributions from IRS Uniform Lifetime Table."""

    def __init__(self) -> None:
        data: dict[str, Any] = load_package_yaml("taxes/tables/rmd_divisors.yaml")
        self._start_age: int = data["rmd_start_age"]
        self._divisors: dict[int, float] = {int(k): float(v) for k, v in data["divisors"].items()}
        self._max_age = max(self._divisors.keys())

    @property
    def start_age(self) -> int:
        """Age when RMDs begin."""
        return self._start_age

    def divisor(self, age: int) -> float:
        """Look up the RMD divisor for a given age."""
        if age < self._start_age:
            return 0.0  # No RMD required
        age = min(age, self._max_age)
        return self._divisors.get(age, self._divisors[self._max_age])

    def compute_rmd(
        self,
        age: int,
        prior_year_balance: NDArray[np.floating[Any]],
    ) -> NDArray[np.floating[Any]]:
        """Compute RMD amount for each path.

        Args:
            age: Current age (integer).
            prior_year_balance: (n_paths,) prior year-end traditional balance.

        Returns:
            (n_paths,) RMD amounts. Zero if age < start_age.
        """
        d = self.divisor(age)
        if d <= 0:
            result: NDArray[np.floating[Any]] = np.zeros_like(prior_year_balance)
            return result
        result = prior_year_balance / d
        return result
