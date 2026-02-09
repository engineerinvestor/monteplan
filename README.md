# monteplan

Monte Carlo financial planning simulator. Supports accumulation and decumulation modeling with realistic taxes, multiple spending policies, multi-asset correlated portfolios, and professional reporting.

Usable as a **Python library**, **CLI**, and **Streamlit web app**.

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### CLI

```bash
monteplan run --config plan.json --output results.json --paths 10000 --seed 42
```

### Python Library

```python
from monteplan.config.schema import PlanConfig, MarketAssumptions, SimulationConfig, PolicyBundle
from monteplan.config.defaults import default_plan, default_market, default_sim_config, default_policies
from monteplan.core.engine import simulate

result = simulate(default_plan(), default_market(), default_policies(), default_sim_config())
print(f"Success probability: {result.success_probability:.1%}")
```

### Streamlit App

```bash
pip install -e ".[app]"
streamlit run app/Home.py
```

## Development

```bash
# Run tests
pytest

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy --strict src/monteplan/

# Benchmarks
pytest --benchmark-only
```

## Disclaimer

This is an educational tool for exploring financial planning concepts. It is **not financial advice**. Results are simulations based on simplified models and assumptions. Consult a qualified financial advisor for real planning decisions.

## License

Apache-2.0
