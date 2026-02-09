"""Shared test fixtures."""

from __future__ import annotations

import pytest
from numpy.random import PCG64DXSM, Generator


@pytest.fixture
def rng() -> Generator:
    """Deterministic RNG for tests."""
    return Generator(PCG64DXSM(42))
