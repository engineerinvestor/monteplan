"""Simple flat-rate tax model for v0.1."""

from __future__ import annotations


class FlatTaxModel:
    """Flat effective tax rate applied to traditional withdrawals and income.

    This is a documented v0.1 simplification. US federal bracket-based
    taxes arrive in v0.2.
    """

    def __init__(self, rate: float = 0.22) -> None:
        self._rate = rate

    def tax_on_income(self, gross_income: float) -> float:
        """Compute tax on earned income."""
        return gross_income * self._rate

    def tax_rate_traditional(self) -> float:
        """Effective tax rate on traditional account withdrawals."""
        return self._rate
