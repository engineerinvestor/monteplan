"""Pydantic v2 configuration models for monteplan."""

from __future__ import annotations

from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiscreteEvent(BaseModel):
    """A one-time financial event at a specific age."""

    model_config = ConfigDict(extra="forbid")

    age: float = Field(ge=18, le=120, description="Age when event occurs")
    amount: float = Field(description="Dollar amount (positive=inflow, negative=outflow)")
    description: str = Field(default="", description="Description of the event")


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
    income_growth_rate: float = Field(
        default=0.0,
        ge=-0.5,
        le=0.5,
        description="Annual real income growth rate (e.g. 0.02 for 2%)",
    )
    discrete_events: list[DiscreteEvent] = Field(
        default_factory=list,
        description="One-time financial events (e.g. home purchase, inheritance)",
    )
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


class GlidePath(BaseModel):
    """Age-based target allocation that shifts over time."""

    model_config = ConfigDict(extra="forbid")

    start_age: int = Field(ge=18, le=120)
    start_weights: list[float] = Field(min_length=1)
    end_age: int = Field(ge=18, le=120)
    end_weights: list[float] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_glide_path(self) -> GlidePath:
        if self.end_age <= self.start_age:
            raise ValueError("end_age must be greater than start_age")
        if len(self.start_weights) != len(self.end_weights):
            raise ValueError("start_weights and end_weights must have same length")
        if abs(sum(self.start_weights) - 1.0) > 1e-6:
            raise ValueError(f"start_weights must sum to 1.0, got {sum(self.start_weights)}")
        if abs(sum(self.end_weights) - 1.0) > 1e-6:
            raise ValueError(f"end_weights must sum to 1.0, got {sum(self.end_weights)}")
        return self


class MarketAssumptions(BaseModel):
    """Market return and inflation assumptions."""

    model_config = ConfigDict(extra="forbid")

    assets: list[AssetClass] = Field(min_length=1)
    expected_annual_returns: list[float]
    annual_volatilities: list[float]
    correlation_matrix: list[list[float]]
    inflation_mean: float = Field(default=0.03, description="Long-run annual inflation rate")
    inflation_vol: float = Field(default=0.01, ge=0, description="Inflation annual volatility")
    return_model: Literal["mvn", "student_t", "bootstrap"] = Field(
        default="mvn",
        description="Return model type",
    )
    degrees_of_freedom: float | None = Field(
        default=None,
        gt=2,
        description="Degrees of freedom for student-t returns",
    )
    historical_returns: list[list[float]] | None = Field(
        default=None,
        description="Historical monthly returns matrix (n_months x n_assets) for bootstrap",
    )
    bootstrap_block_size: int = Field(
        default=12,
        ge=1,
        description="Block size for block bootstrap (months)",
    )
    glide_path: GlidePath | None = Field(
        default=None,
        description="Age-based glide path; when set, overrides static asset weights over time",
    )

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


class StressScenario(BaseModel):
    """A deterministic stress scenario overlay."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Scenario name")
    scenario_type: Literal["crash", "lost_decade", "high_inflation", "sequence_risk"] = Field(
        description="Type of stress scenario",
    )
    start_age: float = Field(ge=18, le=120, description="Age when scenario begins")
    duration_months: int = Field(ge=1, le=360, description="Duration in months")
    severity: float = Field(
        default=1.0,
        gt=0,
        description="Severity multiplier (1.0 = default scenario intensity)",
    )


class SimulationConfig(BaseModel):
    """Simulation execution parameters."""

    model_config = ConfigDict(extra="forbid")

    n_paths: int = Field(default=5000, ge=1, le=1_000_000)
    seed: int = Field(default=42, ge=0)
    store_paths: bool = Field(default=False, description="Store full path data (memory-heavy)")
    stress_scenarios: list[StressScenario] = Field(
        default_factory=list,
        description="Deterministic stress scenarios to apply",
    )


class GuardrailsConfig(BaseModel):
    """Guyton-Klinger guardrails spending policy parameters."""

    model_config = ConfigDict(extra="forbid")

    initial_withdrawal_rate: float = Field(default=0.05, gt=0, le=0.2)
    upper_threshold: float = Field(default=0.20, gt=0, le=1)
    lower_threshold: float = Field(default=0.20, gt=0, le=1)
    raise_pct: float = Field(default=0.10, gt=0, le=1)
    cut_pct: float = Field(default=0.10, gt=0, le=1)


class VPWConfig(BaseModel):
    """Variable Percentage Withdrawal spending policy parameters."""

    model_config = ConfigDict(extra="forbid")

    min_rate: float = Field(default=0.03, ge=0, le=1)
    max_rate: float = Field(default=0.15, ge=0, le=1)


class SpendingPolicyConfig(BaseModel):
    """Spending policy configuration."""

    model_config = ConfigDict(extra="forbid")

    policy_type: Literal[
        "constant_real",
        "percent_of_portfolio",
        "guardrails",
        "vpw",
    ] = "constant_real"
    withdrawal_rate: float = Field(
        default=0.04,
        gt=0,
        le=1,
        description="Annual withdrawal rate for percent_of_portfolio policy",
    )
    guardrails: GuardrailsConfig = Field(default_factory=GuardrailsConfig)
    vpw: VPWConfig = Field(default_factory=VPWConfig)


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
    tax_model: Literal["flat", "us_federal"] = Field(
        default="flat",
        description="Tax model to use",
    )
    tax_rate: float = Field(
        default=0.22,
        ge=0,
        le=1,
        description="Flat effective tax rate (used when tax_model='flat')",
    )
    filing_status: Literal["single", "married_jointly"] = Field(
        default="single",
        description="Tax filing status (used when tax_model='us_federal')",
    )
