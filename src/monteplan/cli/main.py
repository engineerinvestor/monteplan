"""CLI entry point for monteplan."""

from __future__ import annotations

from pathlib import Path

import click

from monteplan.config.defaults import (
    default_market,
    default_plan,
    default_policies,
    default_sim_config,
)
from monteplan.core.engine import simulate
from monteplan.io.serialize import dump_results_summary, load_config


@click.group()
@click.version_option(package_name="monteplan")
def cli() -> None:
    """monteplan — Monte Carlo financial planning simulator."""


@cli.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to JSON config file. Uses defaults if not provided.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to write results JSON.",
)
@click.option("--paths", default=None, type=int, help="Number of simulation paths.")
@click.option("--seed", default=None, type=int, help="Random seed.")
def run(
    config_path: Path | None,
    output_path: Path | None,
    paths: int | None,
    seed: int | None,
) -> None:
    """Run a Monte Carlo simulation."""
    if config_path is not None:
        json_str = config_path.read_text()
        plan, market, policies, sim_config = load_config(json_str)
    else:
        plan = default_plan()
        market = default_market()
        policies = default_policies()
        sim_config = default_sim_config()

    # CLI overrides
    if paths is not None:
        sim_config = sim_config.model_copy(update={"n_paths": paths})
    if seed is not None:
        sim_config = sim_config.model_copy(update={"seed": seed})

    click.echo(f"Running simulation: {sim_config.n_paths} paths, seed={sim_config.seed}")
    click.echo(f"Plan: age {plan.current_age} → {plan.retirement_age} → {plan.end_age}")

    result = simulate(plan, market, policies, sim_config)

    click.echo(f"\nSuccess probability: {result.success_probability:.1%}")
    click.echo("Terminal wealth percentiles:")
    for key, val in sorted(result.terminal_wealth_percentiles.items()):
        click.echo(f"  {key}: ${val:,.0f}")

    if output_path is not None:
        results_json = dump_results_summary(
            result.success_probability,
            result.terminal_wealth_percentiles,
            result.n_paths,
            result.n_steps,
            result.seed,
        )
        output_path.write_text(results_json)
        click.echo(f"\nResults written to {output_path}")


if __name__ == "__main__":
    cli()
