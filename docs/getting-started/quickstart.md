# Quick Start

Three ways to use monteplan: as a Python library, from the command line, or through the interactive web app.

## Python Library

```python
from monteplan.config.defaults import default_plan, default_market, default_policies, default_sim_config
from monteplan.core.engine import simulate

result = simulate(default_plan(), default_market(), default_policies(), default_sim_config())
print(f"Success probability: {result.success_probability:.1%}")
print(f"Median terminal wealth: ${result.terminal_wealth_percentiles['p50']:,.0f}")
```

## CLI

```bash
# Run with defaults (5,000 paths, seed 42)
monteplan run --paths 5000 --seed 42

# Run with a saved config file
monteplan run --config my_plan.json --output results.json
```

## Streamlit App

```bash
pip install monteplan[app]
streamlit run app/Home.py
```

The app provides an interactive UI for configuring plans, running simulations, comparing scenarios, and exporting results.

## What's Next?

- [First Simulation](first-simulation.md) -- Step-by-step walkthrough building a plan from scratch
- [User Guide](../guide/plan-config.md) -- Detailed coverage of every configuration option
- [Notebooks](../notebooks/index.md) -- Interactive tutorials you can run in Google Colab
