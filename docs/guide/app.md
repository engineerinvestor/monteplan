# Streamlit App

monteplan includes a multi-page Streamlit web application for interactive simulation and visualization.

## Installation and Launch

```bash
pip install monteplan[app]
streamlit run app/Home.py
```

## Pages

### Home

The landing page with:

- Project description and disclaimer
- Quick-start template buttons (Default, FIRE, Coast FIRE, Conservative Retiree)
- Clicking a template populates all configuration pages with sensible defaults

### 1. Plan Setup

Configure your financial plan:

- Current age, retirement age, end age
- Monthly income and spending
- Investment accounts (add/remove, set type, balance, contributions)
- Discrete events (one-time inflows/outflows)
- Guaranteed income streams (Social Security, pensions)

### 2. Portfolio

Configure market assumptions and asset allocation:

- Asset classes with weights, returns, and volatilities
- Correlation matrix
- Return model selection (MVN, Student-t, Bootstrap, Regime Switching)
- Regime switching configuration with transition matrix editor
- Glide path setup
- Stress scenario configuration
- Investment fee settings

### 3. Run & Results

Execute simulations and view results:

- Run simulation button with path count and seed inputs
- Success probability display
- Terminal wealth percentile table
- Wealth fan chart (Plotly) showing P5-P95 bands
- Spending fan chart
- Metrics summary
- CSV export button for wealth time series

### 4. Policies

Configure spending, tax, and rebalancing policies:

- Spending policy selector with per-policy parameter controls
- Tax model selection (flat rate or US federal)
- Filing status for US federal model
- Withdrawal ordering (drag to reorder)
- Rebalancing strategy (calendar or threshold)

### 5. Compare Scenarios

Side-by-side scenario comparison:

- Save the current configuration as a named scenario
- Run multiple scenarios and compare
- Overlay fan chart showing all scenarios
- Dominance scatter plot

### 6. Sensitivity

Interactive sensitivity analysis:

- One-at-a-time tornado chart
- Parameter selection
- Perturbation percentage slider
- Results table with sortable columns

## Session State

All configuration is stored in Streamlit session state. There is no database -- data persists only within the browser session. Use the JSON export/import features to save and share configurations.

## Caching

Simulation results are cached using `st.cache_data` keyed by the config hash. Changing any configuration parameter invalidates the cache and triggers a fresh simulation.
