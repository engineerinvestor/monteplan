# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**monteplan** is a Monte Carlo financial planning simulator (Python package + Streamlit web app). It supports accumulation and decumulation modeling with realistic taxes, multiple spending policies, multi-asset correlated portfolios, and professional reporting. The engine is usable as a library, CLI, and web UI.

## Build & Development Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_engine.py
pytest tests/test_engine.py::test_basic_simulation -v

# Type checking
mypy src/monteplan/   # or pyright

# Linting and formatting
ruff check src/ tests/
ruff format src/ tests/

# Run benchmarks
pytest --benchmark-only

# Run the Streamlit app locally
streamlit run app/Home.py

# Build docs
mkdocs serve   # local preview
mkdocs build   # build static site
```

## Architecture

### Separation of Concerns

The project enforces strict separation between three layers:
- **Engine** (`src/monteplan/`): Pure computation, no UI dependencies. This is the installable Python package.
- **App** (`app/`): Streamlit web UI that imports the engine as a library. Never put simulation logic here.
- **Data adapters** (`src/monteplan/io/`): Serialization and optional market data adapters, isolated from both engine and UI.

### Engine Core (`src/monteplan/core/`)

- `engine.py` — Orchestrator: takes a plan config, market assumptions, policies, and simulation config, returns a `SimulationResult`. Entry point: `simulate(plan, market, policies, sim_cfg)`.
- `timeline.py` — Monthly time grid with date/age conversions. Default time step is monthly.
- `state.py` — Mutable simulation state passed through each time step (balances, income, tax status, age).
- `rng.py` — Deterministic RNG via `numpy.random.Generator(PCG64DXSM)`. Every run must be seedable and reproducible.
- `vectorize.py` — Vectorized numpy helpers for fast path evolution.

### Plugin-Style Interfaces

Models and policies are defined via protocols/ABCs so they can be swapped or extended:

- **Return models** (`models/returns/`): `ReturnModel.sample(n_paths, n_steps, rng) -> ndarray[paths, steps, assets]`. Implementations: multivariate normal/t (default), historical bootstrap, regime-switching, factor model.
- **Spending policies** (`policies/spending/`): `SpendingPolicy.compute(state) -> SpendingDecision`. Each policy is independently testable. Implementations: constant real, percent-of-portfolio, floor-and-ceiling, Guyton-Klinger guardrails, VPW.
- **Tax model** (`taxes/`): `TaxModel.compute_taxes(income_events, realized_gains, deductions, state)`. Jurisdiction is pluggable; US federal is the baseline. Tax bracket tables are config-driven YAML/CSV, not hardcoded.

### Config System (`config/`)

- Pydantic or dataclass-based typed configs: `PlanConfig`, `MarketAssumptions`, `SimulationConfig`, `PolicyBundle`.
- Default assumptions in `defaults.yaml`. All configs are exportable/importable as JSON for reproducibility.
- Config hashing is used for caching and result provenance.

### Account Types & Tax Awareness

The engine models taxable, traditional (401k/IRA), Roth, and HSA accounts with distinct tax treatment. Withdrawal ordering policy and RMD integration drive decumulation. Tax bracket tables are stored in `taxes/tables/` as data files.

### Streamlit App (`app/`)

Multi-page Streamlit app with pages numbered for nav ordering (1_Plan_Setup.py through 7_Sensitivity.py). Uses `st.cache_data`/`st.cache_resource` keyed by config hash for simulation results. No database — user data persists only via downloadable config JSON.

## Key Conventions

- **Reproducibility**: Every simulation result embeds `config_hash`, `seed`, and `engine_version`. Golden test snapshots verify deterministic outputs for fixed seeds.
- **Performance**: Vectorized numpy by default; optional numba acceleration (auto-detected). Memory modes: `summary_only=True` stores only percentiles incrementally; `store_paths=False` is the default for web.
- **Testing**: Property-based tests via Hypothesis for invariants (weights sum to 1, no unexpected negative balances). Table-driven tests for tax calculations. Benchmark suite via `pytest-benchmark` to prevent perf regressions.
- **Python version**: >=3.11. CI runs a test matrix across 3.11 and 3.12.
- **Time step**: Monthly by default with annual support. All financial math must handle arithmetic/geometric return conversion consistently.

## Git

- **Remote:** https://github.com/engineerinvestor/monteplan (private)
- **Commit attribution:** Name: Engineer Investor, Email: egr.investor@gmail.com
- **GitHub CLI:** Multiple `gh` accounts are configured. Before pushing, ensure the active account is `engineerinvestor`: `gh auth switch --user engineerinvestor`
