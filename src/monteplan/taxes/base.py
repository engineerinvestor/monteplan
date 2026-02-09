"""Base protocol for tax models."""

from __future__ import annotations

from typing import Protocol


class TaxModel(Protocol):
    """Protocol for tax computation."""

    def tax_on_income(self, gross_income: float) -> float:
        """Compute tax on earned income."""
        ...

    def tax_rate_traditional(self) -> float:
        """Effective tax rate on traditional account withdrawals."""
        ...
