# Sensitivity Analysis

Sensitivity analysis identifies which parameters have the largest impact on your plan's success. monteplan provides two approaches: one-at-a-time (OAT) tornado analysis and 2D heatmaps.

## One-at-a-Time (Tornado) Analysis

Perturbs each parameter independently by +/- a percentage and measures the change in success probability.

```python
from monteplan.analytics.sensitivity import run_sensitivity
from monteplan.config.defaults import default_plan, default_market, default_policies, default_sim_config

report = run_sensitivity(
    plan=default_plan(),
    market=default_market(),
    policies=default_policies(),
    sim_config=default_sim_config(),
    perturbation_pct=0.10,  # +/- 10% perturbation
)

# Results sorted by impact
for r in sorted(report.results, key=lambda x: abs(x.impact), reverse=True):
    print(f"{r.parameter_name}: {r.impact:+.1%} impact "
          f"({r.low_success:.1%} to {r.high_success:.1%})")
```

### Parameters Analyzed

The sensitivity engine automatically builds a registry of perturbable parameters from your plan and market config:

- **Per-asset expected returns** (e.g., `return_US Stocks`)
- **Per-asset volatilities** (e.g., `vol_US Stocks`)
- **Inflation mean and volatility**
- **Monthly spending**
- **Per-account annual contributions**
- **Investment fees** (expense ratio, AUM fee, advisory fee)

### Parallel Execution

Sensitivity analysis supports parallel execution via `ProcessPoolExecutor`:

```python
report = run_sensitivity(
    ...,
    max_workers=4,  # use 4 CPU cores
)
```

## 2D Heatmap Analysis

Explores the interaction between two parameters by sweeping both across a grid.

```python
from monteplan.analytics.sensitivity import run_2d_sensitivity

heatmap = run_2d_sensitivity(
    plan=default_plan(),
    market=default_market(),
    policies=default_policies(),
    sim_config=default_sim_config(),
    x_param="monthly_spending",
    y_param="return_US Stocks",
    x_range=(4000, 6000),
    y_range=(0.05, 0.09),
    x_steps=5,
    y_steps=5,
)

# heatmap.success_grid is a 2D list of success probabilities
print(f"Grid shape: {len(heatmap.y_values)}x{len(heatmap.x_values)}")
```

### Interpreting Results

The heatmap reveals interactions that OAT analysis misses. For example, lower spending combined with higher stock returns might compound to give much higher success rates than either change alone.

## Streamlit App

The Streamlit app (page 6) provides an interactive sensitivity UI with:

- Tornado chart visualization
- Parameter selection checkboxes
- Perturbation percentage slider
- Exportable results

See the [advanced analysis notebook](../notebooks/index.md) for interactive examples.
