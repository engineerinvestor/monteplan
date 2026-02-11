# Changelog

## v0.5

### New Features
- State income tax: flat state tax rate overlay on ordinary income + LTCG
- NIIT (Net Investment Income Tax): 3.8% surtax on investment income above MAGI thresholds
- Roth conversion modeling: fixed amount or fill-to-bracket strategies with configurable age window
- Safe withdrawal rate finder: bisection-based search for maximum spending at target success rate
- Expanded top-level exports: 18+ symbols importable directly from `monteplan`

### Improvements
- Sensitivity analysis supports `policies` target (state tax rate perturbation)
- `USFederalTaxModel.bracket_ceiling()` for fill-bracket Roth conversion strategy
- `USFederalTaxModel.compute_niit_vectorized()` for vectorized NIIT computation

## v0.4

### New Features
- Stress testing: crash, lost decade, high inflation, sequence risk scenarios
- 2D sensitivity heatmaps (`run_sensitivity_heatmap`)
- Plotly-based charts in the Streamlit app (fan chart, spending fan chart, ruin curve, tornado chart)
- Enhanced Streamlit UI with 6 pages and scenario comparison
- Quick-start templates: `fire_plan()`, `coast_fire_plan()`, `conservative_retiree_plan()`
- Full documentation site (MkDocs Material)
- 5 interactive Jupyter notebooks with Colab support
- GitHub Pages deployment

### Improvements
- Polished chart aesthetics with consistent theming
- CSV export for wealth time series
- Config hashing for caching and reproducibility

## v0.3

### New Features
- Per-asset-per-account positions: `(n_paths, n_accounts, n_assets)` 3D array
- 4 return models: MVN, Student-t, Historical Block Bootstrap, Regime Switching
- 5 spending policies: constant real, percent-of-portfolio, guardrails, VPW, floor-and-ceiling
- Tax models: flat (default), US federal (progressive brackets with LTCG)
- Regime switching with 2-5 regimes, transition matrix, and coupled inflation
- Antithetic variates for variance reduction
- Simulation presets: fast (1,000 paths), balanced (5,000), deep (20,000 + antithetic)
- Sensitivity analysis: OAT perturbation engine with parallel execution
- Investment fees: expense ratio, AUM fee, advisory fee
- Guaranteed income streams: Social Security, pensions, annuities with COLA
- Spending time series with percentiles
- Threshold rebalancing
- Metrics: max drawdown distribution, spending volatility, ruin-by-age
- CSV export
- Config hashing via SHA-256

### Infrastructure
- 188 tests passing
- pytest-cov added
- mypy --strict passing

## v0.2

### New Features
- Multi-asset correlated portfolios
- Multiple account types (taxable, traditional, Roth)
- Withdrawal ordering
- Flat tax model
- Click CLI
- JSON config export/import
- Streamlit app (basic)

### Infrastructure
- Pydantic v2 configuration models
- Property-based tests with Hypothesis
- Benchmark suite with pytest-benchmark

## v0.1

### Initial Release
- Basic Monte Carlo engine with monthly time steps
- Single-asset simulation
- Constant real spending policy
- Success probability and terminal wealth percentiles
- Deterministic seeding with PCG64DXSM
