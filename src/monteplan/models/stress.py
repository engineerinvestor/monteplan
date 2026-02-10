"""Stress scenario overlays for return and inflation arrays."""

from __future__ import annotations

import numpy as np

from monteplan.config.schema import StressScenario
from monteplan.core.timeline import Timeline


def apply_stress_scenarios(
    returns: np.ndarray,
    inflation_rates: np.ndarray,
    scenarios: list[StressScenario],
    timeline: Timeline,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply stress scenario overlays to pre-generated returns and inflation.

    Modifies the arrays in-place and also returns them.

    Args:
        returns: (n_paths, n_steps, n_assets) monthly asset returns.
        inflation_rates: (n_paths, n_steps) monthly inflation rates.
        scenarios: List of stress scenarios to apply.
        timeline: Timeline for age-to-step conversion.

    Returns:
        Modified (returns, inflation_rates) tuple.
    """
    for scenario in scenarios:
        start_step = int(round((scenario.start_age - timeline.current_age) * 12))
        end_step = start_step + scenario.duration_months
        start_step = max(0, start_step)
        end_step = min(end_step, timeline.n_steps)

        if start_step >= end_step:
            continue

        severity = scenario.severity

        if scenario.scenario_type == "crash":
            _apply_crash(returns, start_step, end_step, severity)
        elif scenario.scenario_type == "lost_decade":
            _apply_lost_decade(returns, start_step, end_step, severity)
        elif scenario.scenario_type == "high_inflation":
            _apply_high_inflation(inflation_rates, start_step, end_step, severity)
        elif scenario.scenario_type == "sequence_risk":
            _apply_sequence_risk(returns, start_step, end_step, severity)

    return returns, inflation_rates


def _apply_crash(
    returns: np.ndarray,
    start: int,
    end: int,
    severity: float,
) -> None:
    """Apply a crash scenario: sharp decline followed by V-shaped recovery.

    Default (-38% over 12 months at severity=1.0).
    """
    duration = end - start
    half = duration // 2

    # Decline phase: monthly return to achieve total decline
    total_decline = -0.38 * severity
    if half > 0:
        monthly_decline = (1.0 + total_decline) ** (1.0 / half) - 1.0
        returns[:, start : start + half, :] = monthly_decline

    # Recovery phase: return to pre-crash levels
    if duration - half > 0:
        recovery_months = duration - half
        # Recover the full decline
        monthly_recovery = (1.0 / (1.0 + total_decline)) ** (1.0 / recovery_months) - 1.0
        returns[:, start + half : end, :] = monthly_recovery


def _apply_lost_decade(
    returns: np.ndarray,
    start: int,
    end: int,
    severity: float,
) -> None:
    """Apply lost decade: near-zero real returns."""
    # Set returns to ~0% real (just enough to offset nothing)
    returns[:, start:end, :] = 0.001 * (1.0 - severity)  # close to zero


def _apply_high_inflation(
    inflation_rates: np.ndarray,
    start: int,
    end: int,
    severity: float,
) -> None:
    """Apply high inflation: inflation jumps to 6-8% annualized."""
    target_annual = 0.06 + 0.02 * severity  # 6-8% annualized
    monthly_rate = target_annual / 12.0
    inflation_rates[:, start:end] = monthly_rate


def _apply_sequence_risk(
    returns: np.ndarray,
    start: int,
    end: int,
    severity: float,
) -> None:
    """Apply sequence-of-returns risk: poor returns early in period."""
    # First half: severely negative returns
    duration = end - start
    bad_period = min(duration, 60)  # up to 5 years of bad returns
    monthly_bad = -0.02 * severity  # ~-24% annualized
    returns[:, start : start + bad_period, :] = monthly_bad

    # Remainder: above-average returns (partial recovery)
    if duration > bad_period:
        returns[:, start + bad_period : end, :] = 0.01  # ~12% annualized
