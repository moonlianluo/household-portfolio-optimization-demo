# Private input contract

The repository intentionally ships without a research input bundle. Users supply
four files in a directory outside version control.

## `assumptions.json`

Contains `years`, `simulations`, `seed`, `initial_wealth`, and
`tax_deferred_share`.

## `assets.csv`

| Column | Meaning |
|---|---|
| `asset` | Unique research asset identifier |
| `expected_return` | Arithmetic annual return assumption |
| `volatility` | Annual standard deviation |
| `tax_drag` | Simplified annual taxable-account drag assumption |

## `correlations.csv`

A square, symmetric, positive-semidefinite correlation matrix. Row and column
labels must exactly match `assets.csv`.

## `portfolios.csv`

| Column | Meaning |
|---|---|
| `strategy` | Strategy label used in comparisons |
| `account` | `tax_deferred` or `taxable` |
| `asset` | Identifier from `assets.csv` |
| `weight` | Long-only account weight |

Weights must sum to one within each strategy/account pair. The engine accepts
precomputed optimization points but does not contain or infer the optimization
process that created them.

## Research boundary

The engine treats supplied assumptions and weights as user-owned research inputs.
It does not validate suitability, tax law, assumption quality, or permission to
use or disclose those inputs.

