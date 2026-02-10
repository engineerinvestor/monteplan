"""US Federal bracket-based income tax model."""

from __future__ import annotations

import math
from typing import Any

from monteplan.io.yaml_loader import load_package_yaml


class USFederalTaxModel:
    """US Federal income tax with progressive brackets.

    Loads bracket tables from YAML data files. Supports ordinary income
    brackets and long-term capital gains rates.
    """

    def __init__(self, tax_year: int = 2024) -> None:
        data: dict[str, Any] = load_package_yaml(f"taxes/tables/us_federal_{tax_year}.yaml")
        self._standard_deduction: dict[str, float] = data["standard_deduction"]
        self._ordinary_brackets: dict[str, list[list[Any]]] = data["ordinary_brackets"]
        self._ltcg_brackets: dict[str, list[list[Any]]] = data["ltcg_brackets"]

    def _apply_brackets(
        self,
        taxable_income: float,
        brackets: list[list[Any]],
    ) -> float:
        """Compute tax using progressive brackets."""
        if taxable_income <= 0:
            return 0.0
        tax = 0.0
        prev_bound = 0.0
        for upper_bound, rate in brackets:
            if upper_bound is None:
                upper_bound = math.inf
            taxable_in_bracket = min(taxable_income, upper_bound) - prev_bound
            if taxable_in_bracket <= 0:
                break
            tax += taxable_in_bracket * rate
            prev_bound = upper_bound
        return tax

    def standard_deduction(self, filing_status: str) -> float:
        """Return standard deduction for filing status."""
        return self._standard_deduction[filing_status]

    def tax_on_income(self, gross_income: float) -> float:
        """Compute tax on ordinary income (single filer, after standard deduction)."""
        taxable = max(0.0, gross_income - self._standard_deduction["single"])
        return self._apply_brackets(taxable, self._ordinary_brackets["single"])

    def tax_rate_traditional(self) -> float:
        """Approximate effective rate for traditional withdrawals.

        Returns a moderate estimate (22% bracket) for use in gross-up
        calculations during the monthly loop.
        """
        return 0.22

    def compute_annual_tax(
        self,
        ordinary_income: float,
        ltcg: float,
        filing_status: str,
    ) -> float:
        """Compute total annual federal tax.

        Ordinary income is taxed at progressive rates after standard deduction.
        LTCG is taxed at preferential rates based on total taxable income.
        """
        std_ded = self._standard_deduction[filing_status]
        taxable_ordinary = max(0.0, ordinary_income - std_ded)
        ordinary_tax = self._apply_brackets(
            taxable_ordinary, self._ordinary_brackets[filing_status]
        )

        # LTCG brackets are based on taxable income
        # For simplicity, apply LTCG brackets directly to LTCG amount
        ltcg_tax = self._apply_brackets(ltcg, self._ltcg_brackets[filing_status])

        return ordinary_tax + ltcg_tax

    def marginal_rate(self, taxable_income: float, filing_status: str) -> float:
        """Return the marginal ordinary income tax rate at given taxable income."""
        brackets = self._ordinary_brackets[filing_status]
        for upper_bound, rate in brackets:
            if upper_bound is None or taxable_income <= upper_bound:
                return float(rate)
        # Should not reach here; return top rate
        return float(brackets[-1][1])
