"""One-at-a-time (OAT) sensitivity analysis for simulation parameters."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from monteplan.config.schema import (
    MarketAssumptions,
    PlanConfig,
    PolicyBundle,
    SimulationConfig,
)
from monteplan.core.engine import simulate

# Type aliases for getter/setter callables
_Getter = Callable[..., float]
_Setter = Callable[..., Any]


@dataclass(frozen=True)
class SensitivityResult:
    """Result of perturbing a single parameter."""

    parameter_name: str
    base_value: float
    low_value: float
    high_value: float
    base_success: float
    low_success: float
    high_success: float
    impact: float  # high_success - low_success


@dataclass
class SensitivityReport:
    """Full report of one-at-a-time sensitivity analysis."""

    results: list[SensitivityResult] = field(default_factory=list)
    base_success_probability: float = 0.0


@dataclass
class _ParamSpec:
    """Internal spec for a perturbable parameter."""

    getter: _Getter
    setter: _Setter
    is_additive: bool = False
    additive_delta: float = 0.0
    target: str = "market"  # "market" or "plan"


def _make_market_return_setter(idx: int) -> _Setter:
    def setter(m: MarketAssumptions, val: float) -> MarketAssumptions:
        new_returns = list(m.expected_annual_returns)
        new_returns[idx] = val
        return m.model_copy(update={"expected_annual_returns": new_returns})

    return setter


def _make_market_vol_setter(idx: int) -> _Setter:
    def setter(m: MarketAssumptions, val: float) -> MarketAssumptions:
        new_vols = list(m.annual_volatilities)
        new_vols[idx] = val
        return m.model_copy(update={"annual_volatilities": new_vols})

    return setter


def _make_contribution_setter(idx: int) -> _Setter:
    def setter(p: PlanConfig, val: float) -> PlanConfig:
        new_accounts = list(p.accounts)
        new_accounts[idx] = new_accounts[idx].model_copy(
            update={"annual_contribution": max(0.0, val)}
        )
        return p.model_copy(update={"accounts": new_accounts})

    return setter


def _run_one(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
) -> float:
    """Run a single simulation and return success probability.

    Top-level function so it is picklable for ProcessPoolExecutor.
    """
    try:
        result = simulate(plan, market, policies, sim_config)
        return result.success_probability
    except (ValueError, Exception):
        return -1.0  # sentinel for failure


def run_sensitivity(
    plan: PlanConfig,
    market: MarketAssumptions,
    policies: PolicyBundle,
    sim_config: SimulationConfig,
    perturbation_pct: float = 0.10,
    parameters: list[str] | None = None,
    max_workers: int | None = None,
) -> SensitivityReport:
    """Run OAT sensitivity analysis.

    Perturbs each parameter by ±perturbation_pct (or additive for ages)
    and measures the impact on success probability.

    Args:
        plan: Financial plan configuration.
        market: Market assumptions.
        policies: Policy bundle.
        sim_config: Simulation config (n_paths capped at 2000 for speed).
        perturbation_pct: Fractional perturbation (default 10%).
        parameters: Optional list of parameter names to vary. If None,
            uses all default parameters.
        max_workers: Maximum number of parallel workers. ``None`` uses
            all available cores; ``1`` forces sequential execution.

    Returns:
        SensitivityReport with per-parameter results.
    """
    # Cap paths for speed
    capped_paths = min(sim_config.n_paths, 2000)
    base_sim = sim_config.model_copy(update={"n_paths": capped_paths, "preset": None})

    # Base run
    base_result = simulate(plan, market, policies, base_sim)
    base_success = base_result.success_probability

    # Define all perturbable parameters
    all_params: dict[str, _ParamSpec] = {}
    n_assets = len(market.assets)

    # Market return parameters
    for i in range(n_assets):
        asset_name = market.assets[i].name
        all_params[f"{asset_name} Return"] = _ParamSpec(
            getter=lambda m, idx=i: m.expected_annual_returns[idx],
            setter=_make_market_return_setter(i),
            is_additive=False,
        )
        all_params[f"{asset_name} Volatility"] = _ParamSpec(
            getter=lambda m, idx=i: m.annual_volatilities[idx],
            setter=_make_market_vol_setter(i),
            is_additive=False,
        )

    # Inflation
    all_params["Inflation Rate"] = _ParamSpec(
        getter=lambda m: m.inflation_mean,
        setter=lambda m, v: m.model_copy(update={"inflation_mean": v}),
        is_additive=False,
    )

    # Plan parameters
    all_params["Monthly Spending"] = _ParamSpec(
        getter=lambda p: p.monthly_spending,
        setter=lambda p, v: p.model_copy(update={"monthly_spending": v}),
        is_additive=False,
        target="plan",
    )

    all_params["Retirement Age"] = _ParamSpec(
        getter=lambda p: float(p.retirement_age),
        setter=lambda p, v: p.model_copy(update={"retirement_age": int(round(v))}),
        is_additive=True,
        additive_delta=2.0,
        target="plan",
    )

    # Account contributions
    for i, acct in enumerate(plan.accounts):
        if acct.annual_contribution > 0:
            all_params[f"{acct.account_type.title()} Contribution"] = _ParamSpec(
                getter=lambda p, idx=i: p.accounts[idx].annual_contribution,
                setter=_make_contribution_setter(i),
                is_additive=False,
                target="plan",
            )

    # Filter to requested parameters
    if parameters is not None:
        param_set = {k: v for k, v in all_params.items() if k in parameters}
    else:
        param_set = all_params

    # Build all perturbation jobs upfront (picklable tuples)
    # Each job: (param_name, direction, plan, market, policies, sim_config)
    jobs: list[tuple[str, str, PlanConfig, MarketAssumptions, PolicyBundle, SimulationConfig]] = []
    param_vals: dict[str, tuple[float, float, float]] = {}  # name -> (base, low, high)

    for param_name, spec in param_set.items():
        target_obj: PlanConfig | MarketAssumptions = plan if spec.target == "plan" else market
        base_val: float = spec.getter(target_obj)

        if spec.is_additive:
            delta = spec.additive_delta
            low_val = base_val - delta
            high_val = base_val + delta
        else:
            low_val = base_val * (1.0 - perturbation_pct)
            high_val = base_val * (1.0 + perturbation_pct)

        param_vals[param_name] = (base_val, low_val, high_val)

        # Build low perturbation config
        if spec.target == "plan":
            try:
                low_plan: PlanConfig = spec.setter(plan, low_val)
                jobs.append((param_name, "low", low_plan, market, policies, base_sim))
            except (ValueError, Exception):
                jobs.append((param_name, "low_fail", plan, market, policies, base_sim))
        else:
            try:
                low_market: MarketAssumptions = spec.setter(market, low_val)
                jobs.append((param_name, "low", plan, low_market, policies, base_sim))
            except (ValueError, Exception):
                jobs.append((param_name, "low_fail", plan, market, policies, base_sim))

        # Build high perturbation config
        if spec.target == "plan":
            try:
                high_plan: PlanConfig = spec.setter(plan, high_val)
                jobs.append((param_name, "high", high_plan, market, policies, base_sim))
            except (ValueError, Exception):
                jobs.append((param_name, "high_fail", plan, market, policies, base_sim))
        else:
            try:
                high_market: MarketAssumptions = spec.setter(market, high_val)
                jobs.append((param_name, "high", plan, high_market, policies, base_sim))
            except (ValueError, Exception):
                jobs.append((param_name, "high_fail", plan, market, policies, base_sim))

    # Run all perturbation simulations
    results_map: dict[tuple[str, str], float] = {}

    if max_workers == 1:
        # Sequential execution
        for param_name, direction, j_plan, j_market, j_policies, j_sim in jobs:
            if direction.endswith("_fail"):
                results_map[(param_name, direction.replace("_fail", ""))] = base_success
            else:
                results_map[(param_name, direction)] = _run_one(
                    j_plan, j_market, j_policies, j_sim
                )
    else:
        # Parallel execution
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_key: dict[concurrent.futures.Future[float], tuple[str, str]] = {}
            for param_name, direction, j_plan, j_market, j_policies, j_sim in jobs:
                if direction.endswith("_fail"):
                    results_map[(param_name, direction.replace("_fail", ""))] = base_success
                else:
                    future = executor.submit(_run_one, j_plan, j_market, j_policies, j_sim)
                    future_to_key[future] = (param_name, direction)

            for future in concurrent.futures.as_completed(future_to_key):
                key = future_to_key[future]
                success = future.result()
                if success < 0:
                    # Sentinel: simulation failed, use base success
                    results_map[key] = base_success
                else:
                    results_map[key] = success

    # Assemble report in original parameter order
    report = SensitivityReport(base_success_probability=base_success)

    for param_name in param_set:
        base_val, low_val, high_val = param_vals[param_name]
        low_success = results_map.get((param_name, "low"), base_success)
        high_success = results_map.get((param_name, "high"), base_success)

        report.results.append(
            SensitivityResult(
                parameter_name=param_name,
                base_value=base_val,
                low_value=low_val,
                high_value=high_val,
                base_success=base_success,
                low_success=low_success,
                high_success=high_success,
                impact=high_success - low_success,
            )
        )

    return report
