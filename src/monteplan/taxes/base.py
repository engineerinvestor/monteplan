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

    def compute_annual_tax(
        self,
        ordinary_income: float,
        ltcg: float,
        filing_status: str,
    ) -> float:
        """Compute total annual federal tax.

        Args:
            ordinary_income: Gross ordinary income (before standard deduction).
            ltcg: Long-term capital gains.
            filing_status: ``"single"`` or ``"married_jointly"``.

        Returns:
            Total tax liability.
        """
        ...

    def marginal_rate(self, taxable_income: float, filing_status: str) -> float:
        """Marginal ordinary income tax rate at given taxable income."""
        ...
