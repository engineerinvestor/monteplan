"""Simple flat-rate tax model."""

from __future__ import annotations


class FlatTaxModel:
    """Flat effective tax rate applied to traditional withdrawals and income."""

    def __init__(self, rate: float = 0.22) -> None:
        self._rate = rate

    def tax_on_income(self, gross_income: float) -> float:
        """Compute tax on earned income."""
        return gross_income * self._rate

    def tax_rate_traditional(self) -> float:
        """Effective tax rate on traditional account withdrawals."""
        return self._rate

    def compute_annual_tax(
        self,
        ordinary_income: float,
        ltcg: float,
        filing_status: str,
    ) -> float:
        """Compute total annual tax at flat rate."""
        return (ordinary_income + ltcg) * self._rate

    def marginal_rate(self, taxable_income: float, filing_status: str) -> float:
        """Marginal rate is always the flat rate."""
        return self._rate
