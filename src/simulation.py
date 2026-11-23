"""Synthetic demonstration of household-level portfolio coordination.

This module intentionally uses fictional assets and simplified tax mechanics.
It illustrates a research workflow; it is not investment or tax advice and is
not a reproduction of any employer or client model.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ASSETS = ("Growth", "Income", "Diversifier")
EXPECTED_RETURNS = np.array([0.075, 0.045, 0.035])
VOLATILITIES = np.array([0.18, 0.07, 0.10])
CORRELATION = np.array(
    [
        [1.00, 0.20, 0.05],
        [0.20, 1.00, 0.10],
        [0.05, 0.10, 1.00],
    ]
)
TAX_DRAG = np.array([0.004, 0.012, 0.006])


@dataclass(frozen=True)
class Config:
    years: int = 25
    simulations: int = 5_000
    seed: int = 42
    initial_wealth: float = 1_000_000.0
    tax_deferred_share: float = 0.50


def _validate_config(config: Config) -> None:
    if config.years <= 0 or config.simulations <= 0:
        raise ValueError("years and simulations must be positive")
    if config.initial_wealth <= 0:
        raise ValueError("initial wealth must be positive")
    if not 0 < config.tax_deferred_share < 1:
        raise ValueError("tax_deferred_share must be between zero and one")


def strategy_weights() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Return account weights for two fictional strategies.

    Both strategies keep the same 60/30/10 household allocation. The baseline
    repeats that mix in each account. The coordinated strategy locates more of
    the tax-inefficient Income sleeve in the tax-deferred account while keeping
    the combined household exposure unchanged at a 50/50 account split.
    """

    household = np.array([0.60, 0.30, 0.10])
    baseline = (household.copy(), household.copy())
    coordinated = (
        np.array([0.30, 0.60, 0.10]),
        np.array([0.90, 0.00, 0.10]),
    )
    return {"Baseline": baseline, "Coordinated": coordinated}


def simulate(config: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run paired Monte Carlo paths and return yearly and terminal summaries."""

    _validate_config(config)
    rng = np.random.default_rng(config.seed)
    covariance = np.outer(VOLATILITIES, VOLATILITIES) * CORRELATION
    shocks = rng.multivariate_normal(
        EXPECTED_RETURNS, covariance, size=(config.simulations, config.years)
    )
    asset_returns = np.clip(shocks, -0.95, None)

    deferred_initial = config.initial_wealth * config.tax_deferred_share
    taxable_initial = config.initial_wealth - deferred_initial
    yearly_frames: list[pd.DataFrame] = []
    terminal_rows: list[dict[str, float | str]] = []

    for strategy, (deferred_w, taxable_w) in strategy_weights().items():
        deferred = np.full(config.simulations, deferred_initial)
        taxable = np.full(config.simulations, taxable_initial)
        cumulative_tax_drag = np.zeros(config.simulations)

        for year in range(1, config.years + 1):
            period_returns = asset_returns[:, year - 1, :]
            deferred_return = period_returns @ deferred_w
            taxable_gross_return = period_returns @ taxable_w
            taxable_drag_rate = TAX_DRAG @ taxable_w
            annual_tax_drag = taxable * taxable_drag_rate

            deferred *= 1.0 + deferred_return
            taxable *= 1.0 + taxable_gross_return - taxable_drag_rate
            cumulative_tax_drag += annual_tax_drag
            total = deferred + taxable

            yearly_frames.append(
                pd.DataFrame(
                    {
                        "strategy": strategy,
                        "simulation": np.arange(config.simulations),
                        "year": year,
                        "wealth": total,
                        "annual_tax_drag": annual_tax_drag,
                    }
                )
            )

        total = deferred + taxable
        for simulation, wealth in enumerate(total):
            terminal_rows.append(
                {
                    "strategy": strategy,
                    "simulation": simulation,
                    "terminal_wealth": wealth,
                    "cumulative_tax_drag": cumulative_tax_drag[simulation],
                }
            )

    return pd.concat(yearly_frames, ignore_index=True), pd.DataFrame(terminal_rows)


def summarize(terminal: pd.DataFrame) -> pd.DataFrame:
    """Build a compact terminal distribution table."""

    return (
        terminal.groupby("strategy")
        .agg(
            p10_terminal_wealth=("terminal_wealth", lambda s: s.quantile(0.10)),
            median_terminal_wealth=("terminal_wealth", "median"),
            p90_terminal_wealth=("terminal_wealth", lambda s: s.quantile(0.90)),
            mean_cumulative_tax_drag=("cumulative_tax_drag", "mean"),
        )
        .reset_index()
    )


def save_outputs(yearly: pd.DataFrame, terminal: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize(terminal)
    summary.to_csv(output / "summary.csv", index=False)

    quantiles = (
        yearly.groupby(["strategy", "year"])["wealth"]
        .quantile([0.10, 0.50, 0.90])
        .unstack()
        .rename(columns={0.10: "p10", 0.50: "median", 0.90: "p90"})
        .reset_index()
    )
    quantiles.to_csv(output / "wealth_quantiles.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = {"Baseline": "#7f8c8d", "Coordinated": "#1f77b4"}
    for strategy, group in quantiles.groupby("strategy"):
        x = group["year"].to_numpy()
        ax.plot(x, group["median"], label=strategy, color=colors[strategy], lw=2.2)
        ax.fill_between(
            x,
            group["p10"].to_numpy(),
            group["p90"].to_numpy(),
            color=colors[strategy],
            alpha=0.12,
        )
    ax.set_title("Synthetic household wealth paths")
    ax.set_xlabel("Year")
    ax.set_ylabel("Household wealth ($)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output / "wealth_paths.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", type=int, default=25)
    parser.add_argument("--simulations", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    config = Config(years=args.years, simulations=args.simulations, seed=args.seed)
    yearly, terminal = simulate(config)
    save_outputs(yearly, terminal, args.output)
    print(summarize(terminal).to_string(index=False))


if __name__ == "__main__":
    main()

