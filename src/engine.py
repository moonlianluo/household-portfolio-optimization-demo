"""Paired Monte Carlo engine for household research portfolios."""

import numpy as np
import pandas as pd

from .models import ResearchBundle


def simulate(bundle: ResearchBundle) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate annual rebalancing with a transparent taxable-account drag."""
    config = bundle.config
    expected = bundle.assets["expected_return"].to_numpy(dtype=float)
    volatility = bundle.assets["volatility"].to_numpy(dtype=float)
    tax_drag = bundle.assets["tax_drag"].to_numpy(dtype=float)
    covariance = np.outer(volatility, volatility) * bundle.correlation
    rng = np.random.default_rng(config.seed)
    returns = rng.multivariate_normal(
        expected, covariance, size=(config.simulations, config.years), check_valid="raise"
    )
    returns = np.clip(returns, -0.95, None)
    deferred_initial = config.initial_wealth * config.tax_deferred_share
    taxable_initial = config.initial_wealth - deferred_initial
    yearly, terminal = [], []
    for strategy, (deferred_weights, taxable_weights) in bundle.portfolios.items():
        deferred = np.full(config.simulations, deferred_initial, dtype=float)
        taxable = np.full(config.simulations, taxable_initial, dtype=float)
        cumulative_drag = np.zeros(config.simulations, dtype=float)
        for year in range(1, config.years + 1):
            period = returns[:, year - 1, :]
            drag_rate = float(taxable_weights @ tax_drag)
            annual_drag = taxable * drag_rate
            deferred *= 1.0 + period @ deferred_weights
            taxable *= 1.0 + period @ taxable_weights - drag_rate
            cumulative_drag += annual_drag
            yearly.append(pd.DataFrame({
                "strategy": strategy,
                "simulation": np.arange(config.simulations),
                "year": year,
                "deferred_wealth": deferred,
                "taxable_wealth": taxable,
                "household_wealth": deferred + taxable,
                "annual_tax_drag": annual_drag,
                "cumulative_tax_drag": cumulative_drag,
            }))
        terminal.append(pd.DataFrame({
            "strategy": strategy,
            "simulation": np.arange(config.simulations),
            "terminal_wealth": deferred + taxable,
            "terminal_deferred_wealth": deferred,
            "terminal_taxable_wealth": taxable,
            "cumulative_tax_drag": cumulative_drag,
        }))
    return pd.concat(yearly, ignore_index=True), pd.concat(terminal, ignore_index=True)

