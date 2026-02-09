"""Pydantic v2 configuration models for monteplan."""

from __future__ import annotations

from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccountConfig(BaseModel):
    """A single investment account."""

    model_config = ConfigDict(extra="forbid")

    account_type: Literal["taxable", "traditional", "roth"] = "taxable"
    balance: float = Field(ge=0, description="Current balance in dollars")
    annual_contribution: float = Field(
        default=0.0, ge=0, description="Annual contribution in dollars"
    )


class PlanConfig(BaseModel):
    """Core financial plan parameters."""

    model_config = ConfigDict(extra="forbid")

    current_age: int = Field(ge=18, le=100)
    retirement_age: int = Field(ge=18, le=100)
    end_age: int = Field(ge=18, le=120)
    accounts: list[AccountConfig] = Field(min_length=1)
    monthly_income: float = Field(default=0.0, ge=0)
    monthly_spending: float = Field(ge=0)
    income_end_age: int | None = Field(
        default=None, ge=18, le=120, description="Age when earned income stops"
    )

    @model_validator(mode="after")
    def _validate_ages(self) -> PlanConfig:
        if self.retirement_age <= self.current_age:
            raise ValueError("retirement_age must be greater than current_age")
        if self.end_age <= self.retirement_age:
            raise ValueError("end_age must be greater than retirement_age")
        if self.income_end_age is None:
            self.income_end_age = self.retirement_age
        if self.income_end_age > self.end_age:
            raise ValueError("income_end_age must not exceed end_age")
        return self


class AssetClass(BaseModel):
    """An asset class with a target allocation weight."""

    model_config = ConfigDict(extra="forbid")

    name: str
    weight: float = Field(ge=0, le=1)


class MarketAssumptions(BaseModel):
    """Market return and inflation assumptions."""

    model_config = ConfigDict(extra="forbid")

    assets: list[AssetClass] = Field(min_length=1)
    expected_annual_returns: list[float]
    annual_volatilities: list[float]
    correlation_matrix: list[list[float]]
    inflation_mean: float = Field(default=0.03, description="Long-run annual inflation rate")
    inflation_vol: float = Field(default=0.01, ge=0, description="Inflation annual volatility")

    @model_validator(mode="after")
    def _validate_market(self) -> MarketAssumptions:
        n = len(self.assets)
        if len(self.expected_annual_returns) != n:
            raise ValueError(
                f"expected_annual_returns length ({len(self.expected_annual_returns)}) "
                f"must match assets length ({n})"
            )
        if len(self.annual_volatilities) != n:
            raise ValueError(
                f"annual_volatilities length ({len(self.annual_volatilities)}) "
                f"must match assets length ({n})"
            )
        if len(self.correlation_matrix) != n:
            raise ValueError(
                f"correlation_matrix must be {n}x{n}, got {len(self.correlation_matrix)} rows"
            )
        for i, row in enumerate(self.correlation_matrix):
            if len(row) != n:
                raise ValueError(f"correlation_matrix row {i} has length {len(row)}, expected {n}")

        # Validate weights sum to ~1
        total_weight = sum(a.weight for a in self.assets)
        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(f"Asset weights must sum to 1.0, got {total_weight}")

        # Validate correlation matrix is symmetric and has 1s on diagonal
        corr = np.array(self.correlation_matrix)
        if not np.allclose(corr, corr.T, atol=1e-8):
            raise ValueError("Correlation matrix must be symmetric")
        if not np.allclose(np.diag(corr), 1.0, atol=1e-8):
            raise ValueError("Correlation matrix diagonal must be 1.0")

        return self


class SimulationConfig(BaseModel):
    """Simulation execution parameters."""

    model_config = ConfigDict(extra="forbid")

    n_paths: int = Field(default=5000, ge=1, le=1_000_000)
    seed: int = Field(default=42, ge=0)
    store_paths: bool = Field(default=False, description="Store full path data (memory-heavy)")


class SpendingPolicyConfig(BaseModel):
    """Spending policy configuration."""

    model_config = ConfigDict(extra="forbid")

    policy_type: Literal["constant_real", "percent_of_portfolio"] = "constant_real"
    withdrawal_rate: float = Field(
        default=0.04,
        gt=0,
        le=1,
        description="Annual withdrawal rate for percent_of_portfolio policy",
    )


class PolicyBundle(BaseModel):
    """Bundle of all policy configurations."""

    model_config = ConfigDict(extra="forbid")

    spending: SpendingPolicyConfig = Field(default_factory=SpendingPolicyConfig)
    rebalancing_months: list[int] = Field(
        default=[1, 7],
        description="Months (1-12) when rebalancing occurs",
    )
    withdrawal_order: list[Literal["taxable", "traditional", "roth"]] = Field(
        default=["taxable", "traditional", "roth"],
        description="Account withdrawal priority order",
    )
    tax_rate: float = Field(
        default=0.22,
        ge=0,
        le=1,
        description="Flat effective tax rate on traditional withdrawals and income",
    )
