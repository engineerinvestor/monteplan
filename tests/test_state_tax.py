"""Tests for state income tax feature."""

from __future__ import annotations

import pytest

from monteplan.config.defaults import default_market, default_plan, default_policies
from monteplan.config.schema import PolicyBundle, SimulationConfig
from monteplan.core.engine import simulate


class TestStateTaxDefault:
    """State tax rate defaults to 0 and preserves v0.4 behavior."""

    def test_default_is_zero(self) -> None:
        policies = default_policies()
        assert policies.state_tax_rate == 0.0

    def test_golden_unchanged_with_default(self) -> None:
        """Default state_tax_rate=0 produces same result as v0.4 golden."""
        result = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(state_tax_rate=0.0),
            SimulationConfig(n_paths=5000, seed=42),
        )
        assert result.success_probability == pytest.approx(0.4794, abs=0.03)

    def test_config_round_trip(self) -> None:
        policies = PolicyBundle(state_tax_rate=0.05)
        dumped = policies.model_dump_json()
        restored = PolicyBundle.model_validate_json(dumped)
        assert restored.state_tax_rate == pytest.approx(0.05)


class TestStateTaxEffect:
    """State tax lowers success probability."""

    def test_state_tax_lowers_success_us_federal(self) -> None:
        """5% state tax with us_federal should lower success vs 0%."""
        sim = SimulationConfig(n_paths=2000, seed=42)
        base = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="us_federal", state_tax_rate=0.0),
            sim,
        )
        with_state = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="us_federal", state_tax_rate=0.05),
            sim,
        )
        assert with_state.success_probability < base.success_probability

    def test_state_tax_adjusts_grossup_flat(self) -> None:
        """State tax rate should be added to gross-up effective rate for flat model."""
        sim = SimulationConfig(n_paths=2000, seed=42)
        base = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="flat", tax_rate=0.22, state_tax_rate=0.0),
            sim,
        )
        with_state = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="flat", tax_rate=0.22, state_tax_rate=0.05),
            sim,
        )
        # Higher effective rate means more gross-up → lower success
        assert with_state.success_probability <= base.success_probability


class TestStateTaxValidation:
    def test_max_rate(self) -> None:
        policies = PolicyBundle(state_tax_rate=0.15)
        assert policies.state_tax_rate == 0.15

    def test_rejects_over_max(self) -> None:
        with pytest.raises(ValueError):
            PolicyBundle(state_tax_rate=0.20)

    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            PolicyBundle(state_tax_rate=-0.01)
