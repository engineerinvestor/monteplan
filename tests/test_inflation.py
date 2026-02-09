"""Tests for OU inflation model."""

from __future__ import annotations

import numpy as np

from monteplan.models.inflation import OUInflationModel


class TestOUInflation:
    def test_output_shape(self, rng) -> None:  # type: ignore[no-untyped-def]
        model = OUInflationModel()
        result = model.sample(100, 360, rng)
        assert result.shape == (100, 360)

    def test_mean_reversion(self) -> None:
        """Long-run average should converge to theta/12."""
        from numpy.random import PCG64DXSM, Generator

        rng = Generator(PCG64DXSM(42))
        theta = 0.03
        model = OUInflationModel(theta=theta, sigma=0.01, kappa=1.0)
        result = model.sample(10_000, 600, rng)
        # Average of last 120 months across all paths
        late_mean = result[:, -120:].mean()
        assert abs(late_mean - theta / 12.0) < 0.0005

    def test_deterministic(self) -> None:
        from numpy.random import PCG64DXSM, Generator

        model = OUInflationModel()
        r1 = model.sample(10, 12, Generator(PCG64DXSM(42)))
        r2 = model.sample(10, 12, Generator(PCG64DXSM(42)))
        np.testing.assert_array_equal(r1, r2)

    def test_positive_long_run_mean(self) -> None:
        """With positive theta, average rates should be positive."""
        from numpy.random import PCG64DXSM, Generator

        rng = Generator(PCG64DXSM(99))
        model = OUInflationModel(theta=0.025, sigma=0.005, kappa=0.5)
        result = model.sample(5_000, 360, rng)
        assert result.mean() > 0
