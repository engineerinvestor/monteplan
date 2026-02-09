Below is a detailed, “professional-grade” spec for an open-source Python package + a free Streamlit Cloud app that delivers best-in-class Monte Carlo financial planning (accumulation + retirement), with an engine that’s usable as a library, a CLI, and a polished web UI.

---

## Project overview

### Working name

**`monteplan`** (package) + **MontePlan App** (Streamlit)

### Mission

A transparent, extensible, and *correct-by-construction* Monte Carlo simulator for personal financial planning that supports:

* accumulation + decumulation (retirement)
* realistic taxes + account types
* policy-driven spending rules
* multi-asset portfolios with correlation and regime risk
* professional reporting and reproducibility
* a free Streamlit Cloud deployment for interactive use

### Design principles

1. **Separation of concerns**: engine ≠ UI ≠ data adapters.
2. **Reproducible and auditable**: every run is seedable; full config export/import; deterministic tests.
3. **Extensible by plugins**: custom return models, spending rules, tax regimes, and objectives.
4. **Fast enough for web**: vectorized simulation, optional numba, parallel paths, variance reduction.
5. **Honest uncertainty**: no magic “one probability”; show sensitivity, distribution bands, and key drivers.
6. **No dark patterns**: no collection/storage of user financial data by default.

---

## Target users

### Personas

* **DIY investor**: wants success probability, spending, retirement readiness, “what if” scenarios.
* **Power user**: wants policy evaluation (e.g., Guyton-Klinger vs VPW), asset location, taxes.
* **Advisor/analyst**: wants reproducible reports, scenario comparison, assumptions audit trail.
* **Developer/researcher**: wants a robust library with an API, plugins, benchmarks, and tests.

---

## Core capabilities (functional requirements)

## 1) Plan modeling

### Plan timeline

* Time step: **monthly** (default), with support for annual
* Horizon: configurable start/end dates or “until age X”
* Household modeling: single / couple (optional v2), dependents as expense modifiers

### Cash flows

* Earned income: salary + bonuses + RSUs (simplified), with growth and end dates
* Contributions:

  * fixed amount, % of income, employer match rules
  * account-specific contribution limits (pluggable)
* Expenses/spending:

  * baseline spending with inflation linkage
  * discrete events (college, home down payment, car)
  * healthcare shock modeling (simple distribution + optional regime linkage)
* Guaranteed income:

  * Social Security (US module), pensions, annuities
  * start age, COLA rules, survivorship options (v2)

### Accounts and holdings

* Account types: taxable, traditional (401k/IRA), Roth, HSA, 529 (optional)
* Account rules:

  * tax treatment, withdrawal ordering policy, RMDs (US module)
  * asset location policy (heuristic “best effort” + advanced optimizer v2)
* Portfolio:

  * asset allocation by account and/or consolidated
  * glide paths (age-based or time-based)
  * rebalancing policies: calendar, threshold, bands, drift-aware
  * fees: fund expense, AUM fee, advisory fee

---

## 2) Return and macro models (simulation engine)

### Asset return generation modes (user-selectable)

1. **Parametric multivariate model (default)**

   * annualized expected returns + vol + correlation
   * convert to monthly with consistent arithmetic/geom handling
   * innovation distribution options:

     * Gaussian
     * Student-t (fat tails)
     * skewed-t (optional v2)
2. **Historical bootstrap**

   * block bootstrap of monthly returns to preserve autocorrelation
   * optional regime-aware bootstrapping
3. **Factor model (advanced)**

   * simulate factors + loadings for assets
   * optional time-varying volatility
4. **Regime-switching model (advanced)**

   * 2–3 regimes (normal / crisis / high inflation)
   * Markov transition matrix
   * regime-dependent means/covs/inflation

### Inflation model

* default: stochastic inflation with mean reversion (CIR/OU-like)
* optional: historical bootstrap of CPI inflation

### Interest rates (optional v2)

* short rate model for cash/bonds, annuity pricing approximations

### Currency and global assets (optional v2)

* FX process and hedged/unhedged handling

### Tail-risk and stress testing

* deterministic stress scenarios:

  * “2008-style drawdown”, “lost decade”, “high inflation decade”
* shock overlays:

  * one-time crash + recovery shape
  * sequence-of-returns stress at retirement start

---

## 3) Withdrawal and spending policies (decumulation)

Support multiple spending “policies” as first-class objects:

1. **Constant real spending**
2. **Percent-of-portfolio**
3. **Floor-and-ceiling**
4. **Guyton-Klinger decision rules** (classic guardrails)
5. **VPW-like rule** (variable percentage withdrawal)
6. **Required Minimum Distributions** integration for traditional accounts
7. **Dynamic discretionary spending**

   * discretionary cut during drawdowns
   * essentials vs discretionary split

Each policy must:

* accept state (portfolio, age, inflation, market regime, tax status)
* output target spending and withdrawal schedule
* be testable independently

---

## 4) Taxes (must-have for “professional-grade”)

### Tax architecture

* A tax engine that is:

  * **jurisdiction module** (US federal baseline v1)
  * pluggable “state tax” (simple flat/none in v1)
* Tax-aware cashflows:

  * taxable dividends/interest/cap gains models (simplified in v1)
  * ordinary income vs qualified dividends
  * tax-loss harvesting (optional v2)
* Withdrawal ordering + tax impact:

  * Roth vs Traditional vs Taxable drawdown strategy
  * capital gains realization modeling for taxable

### Practical v1 scope (good + realistic)

* US federal brackets (config-driven tables, not hardcoded)
* standard deduction + simple itemization toggle
* payroll taxes optional toggle
* long-term capital gains brackets (simplified)
* RMD tables (config-driven)
* **No** complex AMT/NIIT in v1 (explicitly documented)

---

## 5) Outputs, metrics, and reporting

### Primary success metrics

* **Probability of success** (no ruin by horizon)
* **Probability of meeting spending goal** (if dynamic spending is allowed)
* **Shortfall statistics**: expected shortfall amount, duration of shortfall
* **Terminal wealth distribution**: p5/p25/p50/p75/p95
* **Retirement readiness**: fundedness ratio, “years of spending covered”
* **Utility-based metrics (advanced)**

  * expected CRRA utility
  * certainty-equivalent spending / wealth

### Risk/portfolio diagnostics per path and aggregated

* max drawdown distribution
* time-to-recovery distribution
* volatility of spending (for dynamic policies)
* sequence risk decomposition (e.g., first 5 years after retirement impact)

### Visuals (library + app)

* fan chart of portfolio value over time
* spending path bands over time
* ruin curves by age
* scenario comparison charts (base vs stress vs alternative policy)
* sensitivity tornado chart (returns, inflation, savings rate, retirement age)

### Report artifacts

* export results to:

  * JSON (full config + summary + percentiles)
  * CSV (time series percentiles)
  * PDF/HTML report (optional v2; HTML easiest on Streamlit)

---

## Package architecture (technical spec)

### Repository layout

```
monteplan/
  pyproject.toml
  README.md
  LICENSE
  src/monteplan/
    __init__.py
    config/
      schema.py              # typed configs (pydantic/dataclasses)
      defaults.yaml
      validators.py
    core/
      timeline.py            # monthly grid, date/age conversions
      state.py               # simulation state representation
      engine.py              # orchestrates simulation
      rng.py                 # seeding, streams, reproducibility
      vectorize.py           # fast math helpers
    models/
      returns/
        base.py              # ReturnModel interface
        mvn.py               # Gaussian/t innovations
        bootstrap.py
        regime.py
        factor.py
      macro/
        inflation.py
        rates.py             # optional v2
    policies/
      spending/
        base.py
        constant_real.py
        guardrails.py
        vpw.py
      contributions.py
      rebalancing.py
      withdrawals.py
      asset_location.py      # v2 advanced
    taxes/
      base.py
      us_federal.py
      tables/                # bracket YAML/CSV tables
    analytics/
      metrics.py
      percentiles.py
      attribution.py
      stress.py
    io/
      serialize.py           # config/results JSON
      adapters.py            # market data adapters (optional)
    cli/
      main.py
    utils/
      logging.py
      exceptions.py
  app/                       # Streamlit app
    Home.py
    pages/
      1_Plan_Setup.py
      2_Portfolio.py
      3_Assumptions.py
      4_Policies.py
      5_Run_Results.py
      6_Compare_Scenarios.py
      7_Sensitivity.py
    components/
      charts.py
      forms.py
      caching.py
  tests/
  docs/
```

### Public API (library)

Core objects:

* `PlanConfig`
* `MarketAssumptions`
* `SimulationConfig`
* `PolicyBundle` (spending, rebalancing, withdrawals)
* `simulate(plan, market, policies, sim_cfg) -> SimulationResult`

Key interfaces (protocols / ABCs):

* `ReturnModel.sample(n_paths, n_steps, rng) -> ndarray[paths, steps, assets]`
* `SpendingPolicy.compute(state) -> SpendingDecision`
* `TaxModel.compute_taxes(income_events, realized_gains, deductions, state)`

### Data model (results)

`SimulationResult` must contain:

* `config_hash`, `seed`, `engine_version`
* summary metrics dict
* percentiles time series for:

  * total wealth
  * spending
  * taxes
  * account balances by type (optional)
* per-path optional outputs behind a flag (for memory control)

---

## Performance and scalability requirements

### Constraints (Streamlit Cloud-friendly)

* typical run: **5,000–20,000 paths**, 30–60 year horizon, monthly steps
* target latency: **< 2–6 seconds** for “interactive” preset; longer runs allowed with progress bar

### Performance techniques (required)

* vectorized numpy operations for path evolution
* optional `numba` acceleration (auto-detect)
* variance reduction options:

  * antithetic variates
  * quasi-Monte Carlo (Sobol) optional
* memory modes:

  * `summary_only=True` (store percentiles incrementally)
  * `store_paths=False` default for web
* parallelization:

  * joblib or multiprocessing optional, but keep Streamlit stability in mind (guarded)

### Correctness and reproducibility

* deterministic RNG streams (`numpy.random.Generator(PCG64DXSM)`)
* config hashing and embedding assumptions in exports
* golden test snapshots for known seeds/configs

---

## Streamlit Cloud app spec

### App goals

* allow a user to model a plan in ~5 minutes
* run simulations with sensible presets
* compare strategies (e.g., 60/40 vs 80/20, guardrails vs constant real)
* export a shareable config + results

### Pages & UX flow

1. **Home**

   * what this is / isn’t (not financial advice)
   * quick start templates:

     * “Simple retirement”
     * “FIRE”
     * “Coast FIRE”
     * “Conservative retiree”
2. **Plan Setup**

   * current age, retirement age, horizon
   * income + savings + one-time events
   * baseline spending + inflation linkage
3. **Portfolio**

   * asset classes selection + weights
   * accounts (taxable/trad/Roth), starting balances
   * glide path toggle + rebalancing policy
4. **Assumptions**

   * return model choice (parametric vs historical bootstrap)
   * expected returns/vol/corr editor (with defaults)
   * inflation model and long-run mean
   * fees
5. **Policies**

   * spending rule selection with knobs
   * withdrawal ordering selection
   * tax model toggles
6. **Run & Results**

   * presets: Fast / Balanced / Deep
   * progress + runtime estimate *without promises*
   * key metrics tiles + charts + “what drove results”
7. **Compare Scenarios**

   * side-by-side metrics
   * overlay fan charts
   * “dominance” view (tradeoffs: success vs median spending vs downside)
8. **Sensitivity**

   * one-at-a-time sensitivity sliders
   * tornado chart generator
   * “sequence risk near retirement” stress toggles

### App engineering requirements

* Streamlit caching:

  * cache market data pulls
  * cache simulation results keyed by config hash
* privacy:

  * no database by default
  * provide “download config JSON” for persistence
* export:

  * download results JSON/CSV
  * optional HTML report generation

---

## Documentation and credibility (must-have)

### Documentation

* `docs/` built with MkDocs Material or Sphinx
* “Assumptions & math” section:

  * return model definitions
  * inflation model
  * how taxes are approximated
  * limitations and when not to trust outputs
* Tutorials:

  * “Your first plan”
  * “Guardrails vs constant spending”
  * “Impact of asset allocation”
  * “Sequence risk stress testing”
* Examples:

  * notebooks + script examples
  * reproducible seeds

### Trust features

* “Assumptions audit” panel in app:

  * expected returns/vol/corr
  * inflation assumption
  * fees
  * tax regime toggles
* explicit caveats:

  * “models are simplifications”
  * “results are sensitive to assumptions”

---

## Testing, CI/CD, and release engineering

### Testing strategy

* Unit tests for:

  * timeline math, cashflow scheduling
  * tax calculations (table-driven)
  * spending policies (invariants: floor/ceiling respected)
  * return models (moments approx)
* Property-based tests (Hypothesis):

  * weights sum to 1
  * no negative balances unless allowed
  * monotonicity checks where applicable
* Regression tests:

  * golden output summaries with fixed seed/config

### Quality gates

* mypy/pyright type checking
* ruff formatting/linting
* coverage target: 85%+ for core engine
* benchmark suite (`pytest-benchmark`) to prevent perf regressions

### CI

* GitHub Actions:

  * test matrix (py 3.10–3.12)
  * build docs
  * publish to PyPI on tagged release
* Streamlit Cloud deployment:

  * `app/` points to installed package version (editable install in dev)

---

## Licensing and compliance

* License: **Apache-2.0** (friendly for commercial use + patents) or MIT
* Mandatory disclaimer:

  * educational tool, not financial advice
* No user tracking by default
* Optional anonymous telemetry only if explicitly opt-in (recommended: none)

---

## Implementation roadmap (practical milestones)

### v0.1 (MVP that’s already useful)

* monthly timeline, multi-asset correlated parametric model
* taxable/trad/Roth accounts (simplified)
* constant real spending + percent-of-portfolio
* basic rebalancing
* core success/shortfall metrics
* Streamlit app with config export/import

### v0.2

* guardrails policy + VPW-like policy
* historical bootstrap model
* stress scenarios page
* better tax modeling (US federal tables + RMD)

### v0.3

* regime switching returns/inflation
* variance reduction + fast/deep presets
* scenario comparison + sensitivity tornado

### v1.0 “professional-grade”

* robust tax modules, validated policies, full docs
* plugin system stabilized
* report export (HTML/PDF)
* extensive testing + benchmark suite

---

## Nice-to-have “best-in-class” differentiators

* **Policy optimization**: choose spending rule parameters to maximize utility under constraints
* **Goal-based planning**: multiple goals with priority + dynamic funding
* **Liability matching view**: fundedness of essential spending vs discretionary
* **Explainability that matters**: sensitivity + driver attribution, not “model internals”

---

If you want, I can also generate:

* a complete `pyproject.toml` + scaffolding files,
* the config schema (Pydantic models),
* and a Streamlit app skeleton with all pages wired to a placeholder simulation call.
