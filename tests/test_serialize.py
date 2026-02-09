"""Tests for JSON serialization round-trip."""

from __future__ import annotations

from monteplan.config.defaults import (
    default_market,
    default_plan,
    default_policies,
    default_sim_config,
)
from monteplan.io.serialize import dump_config, load_config


class TestSerialize:
    def test_round_trip(self) -> None:
        """Config should survive JSON round-trip."""
        plan = default_plan()
        market = default_market()
        policies = default_policies()
        sim = default_sim_config()

        json_str = dump_config(plan, market, policies, sim)
        plan2, market2, policies2, sim2 = load_config(json_str)

        assert plan2 == plan
        assert market2 == market
        assert policies2 == policies
        assert sim2 == sim

    def test_golden_file_loads(self) -> None:
        """The golden test config file should load without errors."""
        from pathlib import Path

        golden_path = Path(__file__).parent / "golden" / "basic_retirement.json"
        json_str = golden_path.read_text()
        plan, market, policies, sim = load_config(json_str)
        assert plan.current_age == 30
        assert len(market.assets) == 2
        assert sim.n_paths == 5000
