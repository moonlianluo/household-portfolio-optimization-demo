# Household Portfolio Coordination — Synthetic Research Demo

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A compact, reproducible demonstration of a household portfolio question:

> Can coordinating asset location across taxable and tax-deferred accounts
> improve after-tax outcomes without changing the household's total risk mix?

This public project uses **fictional assets, synthetic capital-market assumptions,
and simplified tax mechanics**. It was independently reconstructed for education
and portfolio demonstration. It contains no employer code, client data, production
parameters, proprietary portfolio weights, or confidential research results.

## Why household-level coordination matters

Two accounts can each look reasonable in isolation while being inefficient when
viewed as one household. The baseline in this demo repeats the same allocation in
both accounts. The coordinated strategy keeps the same combined 60/30/10 exposure
but places more of the tax-inefficient income sleeve in the tax-deferred account.

```text
                         One household objective
                                  |
                    +-------------+-------------+
                    |                           |
          Tax-deferred account           Taxable account
          more income exposure       more growth exposure
                    |                           |
                    +-------------+-------------+
                                  |
                      same total risk allocation
```

## What the demo does

- Generates paired, correlated annual return paths for three fictional assets.
- Compares a repeated-allocation baseline with coordinated asset location.
- Applies a transparent, simplified annual tax-drag assumption to the taxable account.
- Reports terminal-wealth percentiles and cumulative modeled tax drag.
- Produces a reproducible wealth-path chart and CSV summaries.

The paired design means both strategies experience the same simulated market path;
only account placement differs.

## Repository structure

```text
src/simulation.py          Monte Carlo engine and reporting
tests/test_simulation.py   Reproducibility and allocation checks
outputs/                   Generated charts and tables (ignored by Git)
```

## Run locally

```bash
python -m venv .venv
```

Activate the environment, then run:

```bash
python -m pip install -r requirements.txt
python -m src.simulation
```

For a faster smoke test:

```bash
python -m src.simulation --years 10 --simulations 500
```

Generated files:

- `outputs/summary.csv`
- `outputs/wealth_quantiles.csv`
- `outputs/wealth_paths.png`

Run tests with:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Interpretation boundaries

This is a framework demonstration, not an empirical claim that one strategy will
outperform another. The result is mechanically influenced by the fictional return,
volatility, correlation, allocation, and tax-drag assumptions in the source code.
Real household planning would require jurisdiction-specific tax rules, transaction
costs, withdrawals, rebalancing constraints, tax lots, required distributions,
and suitability review.

## Privacy and provenance

This repository is intentionally separate from the private research project that
inspired the general question. Names, datasets, optimization grids, internal
documents, real outputs, and implementation details from that work are excluded.
The public code is a clean-room educational example built from general portfolio
construction concepts.

## License

[MIT](LICENSE). The software is provided for educational purposes without warranty.
