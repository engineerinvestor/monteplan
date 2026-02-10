# Contributing

Contributions are welcome! Here's how to get set up and submit changes.

## Development Setup

```bash
git clone https://github.com/engineerinvestor/monteplan.git
cd monteplan
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# All tests
pytest

# Single file
pytest tests/test_engine.py

# Single test
pytest tests/test_engine.py::test_basic_simulation -v

# With coverage
pytest --cov=monteplan
```

## Code Quality

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking (strict mode)
mypy --strict src/monteplan/
```

All three must pass before merging.

## Code Style

- **Python >= 3.11** features are welcome (match statements, `X | Y` union types, etc.)
- **ruff** rules: `["E", "F", "W", "I", "UP", "B", "SIM"]`
- **mypy --strict** must pass
- **Google-style docstrings** for all public functions and classes
- Line length: 99 characters

## Project Structure

```
src/monteplan/
  core/          # Engine, state, timeline, RNG
  config/        # Pydantic models, defaults
  models/        # Return models, inflation
  policies/      # Spending, rebalancing, withdrawals, contributions
  taxes/         # Tax models, RMD, bracket tables
  analytics/     # Sensitivity analysis, metrics
  io/            # Serialization, YAML loading
  cli/           # Click CLI
app/             # Streamlit web UI
tests/           # Pytest test suite
notebooks/       # Jupyter notebooks
docs/            # MkDocs documentation
```

## Testing Guidelines

- **Property-based tests** (Hypothesis) for invariants (weights sum to 1, no unexpected negative balances)
- **Table-driven tests** for tax calculations
- **Golden tests** for deterministic reproducibility (fixed seed = fixed output)
- **Benchmark suite** via `pytest-benchmark` to prevent performance regressions

## Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes with tests
4. Ensure `pytest`, `ruff check`, `ruff format --check`, and `mypy --strict` all pass
5. Submit a PR with a clear description of the change

## Building Documentation

```bash
pip install -e ".[docs]"
mkdocs serve        # Local preview at http://localhost:8000
mkdocs build        # Build static site
```
