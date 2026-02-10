"""Serialization for configs, results, and time series export."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

from monteplan.config.schema import (
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)


def compute_config_hash(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
) -> str:
    """Compute a deterministic SHA-256 hash of all configs.

    Uses canonical JSON (sorted keys, no whitespace) so the same
    logical config always produces the same hash.
    """
    data = {
        "plan": plan.model_dump(),
        "market": market.model_dump(),
        "policies": policies.model_dump(),
        "simulation": sim_config.model_dump(),
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def dump_config(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
) -> str:
    """Serialize all configs to a JSON string."""
    data = {
        "plan": plan.model_dump(),
        "market": market.model_dump(),
        "policies": policies.model_dump(),
        "simulation": sim_config.model_dump(),
    }
    return json.dumps(data, indent=2)


def load_config(
    json_str: str,
) -> tuple[PlanConfig, MarketAssumptions, PolicyBundle, SimulationConfig]:
    """Deserialize configs from a JSON string."""
    data: dict[str, Any] = json.loads(json_str)
    plan = PlanConfig.model_validate(data["plan"])
    market = MarketAssumptions.model_validate(data["market"])
    policies = PolicyBundle.model_validate(data["policies"])
    sim_config = SimulationConfig.model_validate(data["simulation"])
    return plan, market, policies, sim_config


def dump_time_series_csv(
    time_series: dict[str, list[float]],
    current_age: int,
    end_age: int,
    label: str = "Value",
) -> str:
    """Export time series percentiles as CSV.

    Args:
        time_series: Dict with keys p5, p25, p50, p75, p95, mean.
        current_age: Starting age.
        end_age: Ending age.
        label: Column label prefix (e.g. "Wealth" or "Spending").

    Returns:
        CSV string with Age, P5, P25, P50, P75, P95, Mean columns.
    """
    n_points = len(time_series.get("p50", []))
    if n_points == 0:
        return ""

    step = (end_age - current_age) / max(n_points - 1, 1)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Age",
            f"{label}_P5",
            f"{label}_P25",
            f"{label}_P50",
            f"{label}_P75",
            f"{label}_P95",
            f"{label}_Mean",
        ]
    )

    for i in range(n_points):
        age = current_age + i * step
        row = [
            f"{age:.2f}",
            f"{time_series.get('p5', [0])[i]:.2f}",
            f"{time_series.get('p25', [0])[i]:.2f}",
            f"{time_series['p50'][i]:.2f}",
            f"{time_series.get('p75', [0])[i]:.2f}",
            f"{time_series.get('p95', [0])[i]:.2f}",
            f"{time_series.get('mean', [0])[i]:.2f}",
        ]
        writer.writerow(row)

    return output.getvalue()


def dump_results_summary(
    success_probability: float,
    terminal_wealth_percentiles: dict[str, float],
    n_paths: int,
    n_steps: int,
    seed: int,
) -> str:
    """Serialize simulation results summary to JSON."""
    data = {
        "success_probability": success_probability,
        "terminal_wealth_percentiles": terminal_wealth_percentiles,
        "n_paths": n_paths,
        "n_steps": n_steps,
        "seed": seed,
    }
    return json.dumps(data, indent=2)
