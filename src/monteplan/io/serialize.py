"""JSON serialization for configs and results."""

from __future__ import annotations

import hashlib
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
