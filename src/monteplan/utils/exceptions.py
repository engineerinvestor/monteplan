"""Custom exceptions for monteplan."""

from __future__ import annotations


class MonteplanError(Exception):
    """Base exception for monteplan."""


class ConfigError(MonteplanError):
    """Invalid configuration."""


class SimulationError(MonteplanError):
    """Error during simulation."""
