"""Tests for terminal wealth reported in today's dollars.

Terminal wealth has always been nominal at ``end_age``. Over a multi-decade horizon that
is a far larger number than the same wealth in present terms, and nothing in the result
said so — which is an easy way for a reader to mistake one for the other.

The subtle part, and the reason this belongs in the engine rather than in a caller: the
deflator varies by path, so the real percentiles cannot be recovered from the nominal ones.
``test_real_percentiles_are_not_recoverable_from_nominal`` is the test that pins that.
"""

from __future__ import annotations

import numpy as np
import pytest

from monteplan.config.defaults import default_market, default_plan, default_policies
from monteplan.config.schema import MarketAssumptions, SimulationConfig
from monteplan.core.engine import simulate

KEYS = ["p5", "p25", "p50", "p75", "p95"]


def _run(market: MarketAssumptions | None = None, n_paths: int = 400) -> object:
    return simulate(
        default_plan(),
        market or default_market(),
        default_policies(),
        SimulationConfig(n_paths=n_paths, seed=42),
    )


def _zero_inflation() -> MarketAssumptions:
    return default_market().model_copy(update={"inflation_mean": 0.0, "inflation_vol": 0.0})


# --- the fields exist and are well formed ---


def test_real_percentiles_are_populated() -> None:
    result = _run()
    assert set(result.terminal_wealth_real_percentiles) == set(KEYS)


def test_real_percentiles_are_ordered() -> None:
    result = _run()
    values = [result.terminal_wealth_real_percentiles[k] for k in KEYS]
    assert values == sorted(values)


def test_terminal_inflation_has_one_factor_per_path() -> None:
    result = _run(n_paths=250)
    assert result.terminal_inflation is not None
    assert result.terminal_inflation.shape == (result.n_paths,)


def test_terminal_inflation_is_a_growth_factor_not_a_rate() -> None:
    """It compounds from 1.0, so a long horizon under positive inflation exceeds 1."""
    result = _run()
    assert np.all(result.terminal_inflation > 1.0)


# --- the relationship to the nominal figures ---


def test_real_is_below_nominal_when_inflation_is_positive() -> None:
    """Strictly below wherever there is wealth to deflate.

    A depleted percentile is zero in both, since dividing zero by any deflator leaves
    zero — so the comparison is only strict where the nominal figure is positive.
    """
    result = _run()
    positive = 0
    for key in KEYS:
        nominal = result.terminal_wealth_percentiles[key]
        real = result.terminal_wealth_real_percentiles[key]
        assert real <= nominal
        if nominal > 0:
            assert real < nominal
            positive += 1
    assert positive, "no positive percentile to compare"


def test_real_equals_nominal_when_inflation_is_zero() -> None:
    """With no inflation the deflator is 1.0 on every path, so the two coincide."""
    result = _run(market=_zero_inflation())
    assert np.allclose(result.terminal_inflation, 1.0)
    for key in KEYS:
        assert result.terminal_wealth_real_percentiles[key] == pytest.approx(
            result.terminal_wealth_percentiles[key]
        )


def test_real_percentiles_are_not_recoverable_from_nominal() -> None:
    """The whole reason this lives in the engine.

    A caller holding only the nominal percentiles and a median inflation factor cannot
    reconstruct the real ones, because the median of a ratio is not the ratio of the
    medians when the denominator varies across paths.
    """
    result = _run(n_paths=2000)
    naive = result.terminal_wealth_percentiles["p50"] / float(np.median(result.terminal_inflation))
    exact = result.terminal_wealth_real_percentiles["p50"]
    assert exact != pytest.approx(naive, rel=1e-6)


def test_deflating_is_done_per_path_before_taking_percentiles() -> None:
    """Reproduce the engine's arithmetic from the stored paths."""
    result = simulate(
        default_plan(),
        default_market(),
        default_policies(),
        SimulationConfig(n_paths=300, seed=7, store_paths=True),
    )
    assert result.all_paths is not None
    expected = np.percentile(result.all_paths[:, -1] / result.terminal_inflation, 50)
    assert result.terminal_wealth_real_percentiles["p50"] == pytest.approx(float(expected))


def test_nominal_percentiles_are_unchanged_by_the_addition() -> None:
    """The existing contract must not move."""
    result = simulate(
        default_plan(),
        default_market(),
        default_policies(),
        SimulationConfig(n_paths=300, seed=7, store_paths=True),
    )
    expected = np.percentile(result.all_paths[:, -1], 50)
    assert result.terminal_wealth_percentiles["p50"] == pytest.approx(float(expected))


def test_terminal_inflation_is_a_copy_not_a_live_reference() -> None:
    """Mutating the returned array must not be able to corrupt anything upstream."""
    result = _run(n_paths=100)
    before = result.terminal_wealth_real_percentiles["p50"]
    result.terminal_inflation[:] = 1.0
    assert result.terminal_wealth_real_percentiles["p50"] == before
