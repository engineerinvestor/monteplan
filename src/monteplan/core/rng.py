"""Deterministic RNG factory for reproducible simulations."""

from __future__ import annotations

from numpy.random import PCG64DXSM, Generator


def make_rng(seed: int) -> Generator:
    """Create a deterministic numpy Generator from a seed.

    Uses PCG64DXSM for high-quality, reproducible random number generation.
    """
    return Generator(PCG64DXSM(seed))
