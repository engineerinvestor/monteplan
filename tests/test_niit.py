"""Tests for Net Investment Income Tax (NIIT) feature."""

from __future__ import annotations

import numpy as np
import pytest

from monteplan.config.defaults import default_market, default_plan
from monteplan.config.schema import PolicyBundle, SimulationConfig
from monteplan.core.engine import simulate
from monteplan.taxes.us_federal import USFederalTaxModel


class TestNIITComputation:
    """Unit tests for compute_niit_vectorized."""

    def setup_method(self) -> None:
        self.model = USFederalTaxModel()

    def test_below_threshold_zero(self) -> None:
        """Income below $200K single → $0 NIIT."""
        ordinary = np.array([100_000.0])
        ltcg = np.array([50_000.0])
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "single")
        assert niit[0] == pytest.approx(0.0)

    def test_above_threshold_full_ltcg(self) -> None:
        """MAGI well above threshold, all LTCG taxed."""
        ordinary = np.array([250_000.0])
        ltcg = np.array([30_000.0])
        # MAGI = 280K, excess = 80K, min(30K, 80K) = 30K
        expected = 30_000.0 * 0.038
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "single")
        assert niit[0] == pytest.approx(expected)

    def test_partial_ltcg(self) -> None:
        """MAGI crosses threshold mid-LTCG — only excess portion taxed."""
        ordinary = np.array([180_000.0])
        ltcg = np.array([50_000.0])
        # MAGI = 230K, excess over 200K = 30K, min(50K, 30K) = 30K
        expected = 30_000.0 * 0.038
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "single")
        assert niit[0] == pytest.approx(expected)

    def test_married_threshold(self) -> None:
        """Married filing jointly uses $250K threshold."""
        ordinary = np.array([200_000.0])
        ltcg = np.array([100_000.0])
        # MAGI = 300K, excess over 250K = 50K, min(100K, 50K) = 50K
        expected = 50_000.0 * 0.038
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "married_jointly")
        assert niit[0] == pytest.approx(expected)

    def test_vectorized_multiple_paths(self) -> None:
        """Vectorized across multiple paths."""
        ordinary = np.array([100_000.0, 250_000.0, 180_000.0])
        ltcg = np.array([50_000.0, 30_000.0, 50_000.0])
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "single")
        assert niit[0] == pytest.approx(0.0)
        assert niit[1] == pytest.approx(30_000.0 * 0.038)
        assert niit[2] == pytest.approx(30_000.0 * 0.038)

    def test_zero_ltcg(self) -> None:
        """No LTCG → no NIIT regardless of income."""
        ordinary = np.array([500_000.0])
        ltcg = np.array([0.0])
        niit = self.model.compute_niit_vectorized(ordinary, ltcg, "single")
        assert niit[0] == pytest.approx(0.0)


class TestNIITIntegration:
    """Integration tests for NIIT in the engine."""

    def test_default_disabled(self) -> None:
        """Default include_niit=False produces identical results to v0.4."""
        result = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(include_niit=False),
            SimulationConfig(n_paths=5000, seed=42),
        )
        assert result.success_probability == pytest.approx(0.4794, abs=0.03)

    def test_niit_lowers_success(self) -> None:
        """Enabling NIIT with us_federal should lower success."""
        sim = SimulationConfig(n_paths=2000, seed=42)
        base = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="us_federal", include_niit=False),
            sim,
        )
        with_niit = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="us_federal", include_niit=True),
            sim,
        )
        assert with_niit.success_probability <= base.success_probability

    def test_niit_only_with_us_federal(self) -> None:
        """NIIT flag with flat tax model is ignored (no crash, no effect)."""
        sim = SimulationConfig(n_paths=500, seed=42)
        base = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="flat", include_niit=False),
            sim,
        )
        with_flag = simulate(
            default_plan(),
            default_market(),
            PolicyBundle(tax_model="flat", include_niit=True),
            sim,
        )
        # Flat model never triggers the NIIT block, so results are identical
        assert with_flag.success_probability == pytest.approx(
            base.success_probability, abs=0.001
        )
