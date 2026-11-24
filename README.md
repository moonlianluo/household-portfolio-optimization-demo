# Household Portfolio Research Engine

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reusable simulation and path-dashboard engine for comparing household-level
portfolio strategies across taxable and tax-deferred accounts.

This repository provides **research infrastructure, not a portfolio product**.
It intentionally excludes capital-market assumptions, optimized weights, client
data, production configurations, and the optimization process used to create
portfolio points. Researchers bring their own authorized inputs through a
documented file contract.

## Research workflow

```text
private research inputs
  ├─ asset assumptions
  ├─ correlation matrix
  ├─ strategy/account weights
  └─ simulation assumptions
              │
              ▼
       validation layer
              │
              ▼
    paired Monte Carlo engine
              │
       ┌──────┴────────┐
       ▼               ▼
 summary tables   path dashboard
```

## What is public

- Strict input validation and alignment checks
- Paired multivariate Monte Carlo simulation
- Annual account-level rebalancing
- Transparent taxable-account drag overlay
- Terminal distribution summaries and run manifest
- Standalone interactive HTML path dashboard
- Reproducibility and reporting tests

## What is deliberately not public

- Institutional or employer data
- Actual optimized portfolio points
- Expected-return, volatility, correlation, or tax assumptions
- Optimization objectives, constraints, solver configuration, or production code
- Client information and historical research outputs

The engine can consume precomputed optimization points, but it neither contains
nor reconstructs the process used to produce them.

## Input contract

Prepare a private directory containing:

```text
assumptions.json
assets.csv
correlations.csv
portfolios.csv
```

See [the full input contract](docs/input-contract.md). No example input bundle is
committed, so cloning the repository does not provide recommendations or
institutional research assumptions.

## Run a research bundle

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m src.simulation --input-dir /path/to/private-inputs --output outputs
```

Outputs include `summary.csv`, `wealth_quantiles.csv`, `run_manifest.csv`,
and a standalone `path_dashboard.html`.

## Validate the engine

Tests create a temporary synthetic bundle at runtime; the fixture never becomes
a repository input dataset.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Modeling boundaries

The public engine uses arithmetic annual assumptions, long-only weights, annual
rebalancing, and a simplified asset-level tax-drag overlay. It does not model
tax lots, transaction costs, withdrawals, required distributions, wash-sale
rules, jurisdiction-specific taxes, or investment suitability. Those omissions
are explicit extension points rather than implied production readiness.

## Privacy and provenance

This is a clean-room public implementation of a general household research
workflow. It does not copy private inputs, optimized points, internal documents,
production results, or confidential optimization logic.

## License

[MIT](LICENSE). Educational and research use only; no investment or tax advice.
