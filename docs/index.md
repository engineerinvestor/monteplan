# monteplan

**Monte Carlo financial planning simulator for Python.**

monteplan models accumulation and decumulation with realistic taxes, multiple spending policies, multi-asset correlated portfolios, and professional reporting. Use it as a Python library, CLI tool, or interactive Streamlit web app.

---

## Key Features

- **Monte Carlo Engine** -- Vectorized numpy simulation with monthly time steps and deterministic seeding
- **4 Return Models** -- Multivariate normal, Student-t (fat tails), historical block bootstrap, Markov regime switching
- **5 Spending Policies** -- Constant real, percent-of-portfolio, Guyton-Klinger guardrails, VPW, floor-and-ceiling
- **Tax-Aware Withdrawals** -- US federal progressive brackets, LTCG rates, RMD enforcement, configurable withdrawal ordering
- **Multi-Account Support** -- Taxable, traditional (401k/IRA), and Roth accounts with distinct tax treatment
- **Guaranteed Income** -- Social Security, pensions, and annuities with COLA adjustments
- **Stress Testing** -- Market crashes, lost decades, high inflation, and sequence-of-returns risk scenarios
- **Sensitivity Analysis** -- One-at-a-time tornado charts and 2D heatmaps
- **Antithetic Variates** -- Variance reduction for tighter confidence intervals
- **Streamlit App** -- Interactive web UI with Plotly charts, scenario comparison, and CSV export

---

## Quick Start

```python
from monteplan.config.defaults import default_plan, default_market, default_policies, default_sim_config
from monteplan.core.engine import simulate

result = simulate(default_plan(), default_market(), default_policies(), default_sim_config())
print(f"Success probability: {result.success_probability:.1%}")
```

See the [Installation](getting-started/installation.md) guide to get started, or jump straight to the [First Simulation](getting-started/first-simulation.md) walkthrough.

---

## Try It Now

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/engineerinvestor/monteplan/blob/main/notebooks/01_getting_started.ipynb)

---

## Documentation Overview

| Section | Description |
|---|---|
| [Getting Started](getting-started/installation.md) | Installation, quick start, first simulation walkthrough |
| [User Guide](guide/plan-config.md) | Detailed coverage of every feature |
| [Notebooks](notebooks/index.md) | Interactive Colab-ready tutorials and case studies |
| [Case Studies](case-studies/index.md) | Real-world planning scenarios with analysis |
| [Math & Assumptions](math/return-models.md) | Model formulas, assumptions, and limitations |
| [API Reference](api/engine.md) | Auto-generated from source docstrings |

---

!!! warning "Disclaimer"
    This is an educational tool for exploring financial planning concepts. It is **not financial advice**. Results are simulations based on simplified models and assumptions. Consult a qualified financial advisor for real planning decisions.
