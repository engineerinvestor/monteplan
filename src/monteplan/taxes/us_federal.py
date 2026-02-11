"""US Federal bracket-based income tax model."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

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

    def _apply_brackets_vectorized(
        self,
        taxable_income: NDArray[np.floating[Any]],
        brackets: list[list[Any]],
    ) -> NDArray[np.floating[Any]]:
        """Vectorized progressive bracket computation across all paths."""
        tax: NDArray[np.floating[Any]] = np.zeros_like(taxable_income)
        prev_bound = 0.0
        for upper_bound, rate in brackets:
            if upper_bound is None:
                upper_bound = np.inf
            taxable_in_bracket = np.minimum(taxable_income, upper_bound) - prev_bound
            tax += np.maximum(taxable_in_bracket, 0.0) * rate
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

    def compute_annual_tax_vectorized(
        self,
        ordinary_income: NDArray[np.floating[Any]],
        ltcg: NDArray[np.floating[Any]],
        filing_status: str,
    ) -> NDArray[np.floating[Any]]:
        """Vectorized annual tax across all paths.

        Args:
            ordinary_income: (n_paths,) ordinary income per path.
            ltcg: (n_paths,) long-term capital gains per path.
            filing_status: Filing status key.

        Returns:
            (n_paths,) total tax liability per path.
        """
        std_ded = self._standard_deduction[filing_status]
        taxable_ordinary = np.maximum(ordinary_income - std_ded, 0.0)
        ordinary_tax = self._apply_brackets_vectorized(
            taxable_ordinary, self._ordinary_brackets[filing_status]
        )
        ltcg_tax = self._apply_brackets_vectorized(ltcg, self._ltcg_brackets[filing_status])
        result: NDArray[np.floating[Any]] = ordinary_tax + ltcg_tax
        return result

    _NIIT_RATE: float = 0.038
    _NIIT_THRESHOLDS: dict[str, float] = {
        "single": 200_000,
        "married_jointly": 250_000,
    }

    def compute_niit_vectorized(
        self,
        ordinary_income: NDArray[np.floating[Any]],
        ltcg: NDArray[np.floating[Any]],
        filing_status: str,
    ) -> NDArray[np.floating[Any]]:
        """Compute Net Investment Income Tax (3.8% surtax).

        NIIT applies to the lesser of net investment income (here approximated
        as LTCG) or the excess of MAGI over the threshold.

        Args:
            ordinary_income: (n_paths,) ordinary income per path.
            ltcg: (n_paths,) long-term capital gains per path.
            filing_status: Filing status key.

        Returns:
            (n_paths,) NIIT liability per path.
        """
        threshold = self._NIIT_THRESHOLDS[filing_status]
        magi = ordinary_income + ltcg
        excess = np.maximum(magi - threshold, 0.0)
        result: NDArray[np.floating[Any]] = np.minimum(ltcg, excess) * self._NIIT_RATE
        return result

    def bracket_ceiling(self, target_rate: float, filing_status: str) -> float:
        """Return the gross income ceiling for a target marginal rate.

        Returns the maximum gross income (bracket upper bound + standard
        deduction) at which the marginal rate is still at or below
        ``target_rate``. Used by fill_bracket Roth conversion strategy.

        Args:
            target_rate: Target marginal tax rate (e.g. 0.22 for 22% bracket).
            filing_status: Filing status key.

        Returns:
            Maximum gross income before exceeding the target bracket.
        """
        std_ded = self._standard_deduction[filing_status]
        brackets = self._ordinary_brackets[filing_status]
        ceiling = 0.0
        for upper_bound, rate in brackets:
            if rate > target_rate:
                break
            ceiling = 10_000_000.0 if upper_bound is None else float(upper_bound)
        return ceiling + std_ded

    def marginal_rate(self, taxable_income: float, filing_status: str) -> float:
        """Return the marginal ordinary income tax rate at given taxable income."""
        brackets = self._ordinary_brackets[filing_status]
        for upper_bound, rate in brackets:
            if upper_bound is None or taxable_income <= upper_bound:
                return float(rate)
        # Should not reach here; return top rate
        return float(brackets[-1][1])
