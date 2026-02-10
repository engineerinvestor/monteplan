# Stress Testing

Stress scenarios overlay deterministic market shocks onto the stochastic simulation, letting you test how your plan survives specific adverse events.

## Scenario Types

### Market Crash

A sudden portfolio drop (like 2008) followed by a V-shaped recovery.

```python
from monteplan.config.schema import StressScenario

crash = StressScenario(
    name="Crash at Retirement",
    scenario_type="crash",
    start_age=65,
    duration_months=12,
    severity=1.0,  # ~38% peak drawdown at severity=1.0
)
```

### Lost Decade

A prolonged period of flat or near-zero real returns.

```python
lost_decade = StressScenario(
    name="Lost Decade",
    scenario_type="lost_decade",
    start_age=65,
    duration_months=120,  # 10 years
    severity=1.0,
)
```

### High Inflation

Elevated inflation rates above normal levels.

```python
high_inflation = StressScenario(
    name="1970s Inflation",
    scenario_type="high_inflation",
    start_age=65,
    duration_months=60,  # 5 years
    severity=1.0,
)
```

### Sequence of Returns Risk

Poor returns in the first years of retirement (the most dangerous period for retirees).

```python
sequence_risk = StressScenario(
    name="Bad Sequence",
    scenario_type="sequence_risk",
    start_age=65,
    duration_months=36,  # 3 years of bad returns
    severity=1.0,
)
```

## Adding Stress Scenarios to a Simulation

Scenarios are added to `SimulationConfig`:

```python
from monteplan.config.schema import SimulationConfig

sim_config = SimulationConfig(
    n_paths=5000,
    seed=42,
    stress_scenarios=[crash, high_inflation],
)
```

Multiple scenarios can be applied simultaneously. They are overlaid onto the stochastically generated return and inflation paths.

## Severity Parameter

The `severity` parameter scales the intensity of each scenario:

- `severity=0.5` -- Half the default shock magnitude
- `severity=1.0` -- Default magnitude (calibrated to historical events)
- `severity=2.0` -- Double the default magnitude

## Comparing Stressed vs Base Scenarios

Run the same plan with and without stress scenarios to measure the impact:

```python
from monteplan.core.engine import simulate
from monteplan.config.defaults import default_plan, default_market, default_policies

plan = default_plan()
market = default_market()
policies = default_policies()

# Base case
base_result = simulate(plan, market, policies, SimulationConfig(n_paths=5000, seed=42))

# Stressed case
stressed_result = simulate(plan, market, policies, SimulationConfig(
    n_paths=5000, seed=42,
    stress_scenarios=[
        StressScenario(name="Crash", scenario_type="crash", start_age=65, duration_months=12),
    ],
))

print(f"Base success: {base_result.success_probability:.1%}")
print(f"Stressed success: {stressed_result.success_probability:.1%}")
```

## Stress Testing Tips

- **Test crashes at retirement** -- Sequence-of-returns risk is most dangerous right as spending begins
- **Combine scenarios** -- A crash followed by high inflation is worse than either alone
- **Use with different spending policies** -- Adaptive policies (guardrails, VPW) handle stress better than constant real spending
- **Pair with sensitivity analysis** -- Use stress tests for specific scenarios, sensitivity for parameter exploration
