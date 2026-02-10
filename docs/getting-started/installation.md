# Installation

## From PyPI

```bash
pip install monteplan
```

## From GitHub (latest)

```bash
pip install "monteplan @ git+https://github.com/engineerinvestor/monteplan.git"
```

## Editable Development Install

Clone the repo and install with dev dependencies:

```bash
git clone https://github.com/engineerinvestor/monteplan.git
cd monteplan
pip install -e ".[dev]"
```

## Streamlit App

To run the interactive web app, install the `app` extras:

```bash
pip install -e ".[app]"
streamlit run app/Home.py
```

## Google Colab

Run this in the first cell of a Colab notebook:

```python
!pip install -q "monteplan @ git+https://github.com/engineerinvestor/monteplan.git"
```

## Requirements

- Python >= 3.11
- Core dependencies: numpy, scipy, pydantic, click, pyyaml

## Optional Dependency Groups

| Group | Install | Includes |
|---|---|---|
| `dev` | `pip install -e ".[dev]"` | pytest, hypothesis, mypy, ruff, benchmarks |
| `app` | `pip install -e ".[app]"` | streamlit, plotly |
| `docs` | `pip install -e ".[docs]"` | mkdocs, mkdocs-material, mkdocstrings |
