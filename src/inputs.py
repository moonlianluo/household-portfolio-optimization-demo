"""Load and validate a user-owned research input bundle."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .models import ResearchBundle, SimulationConfig

ASSET_COLUMNS = ("asset", "expected_return", "volatility", "tax_drag")
PORTFOLIO_COLUMNS = ("strategy", "account", "asset", "weight")
ACCOUNTS = ("tax_deferred", "taxable")


def _load_config(path: Path) -> SimulationConfig:
    values = json.loads(path.read_text(encoding="utf-8"))
    required = {"years", "simulations", "seed", "initial_wealth", "tax_deferred_share"}
    missing = required - values.keys()
    if missing:
        raise ValueError(f"assumptions.json is missing: {sorted(missing)}")
    config = SimulationConfig(**{key: values[key] for key in required})
    if config.years <= 0 or config.simulations <= 0:
        raise ValueError("years and simulations must be positive")
    if config.initial_wealth <= 0:
        raise ValueError("initial_wealth must be positive")
    if not 0 < config.tax_deferred_share < 1:
        raise ValueError("tax_deferred_share must be between zero and one")
    return config


def _load_assets(path: Path) -> pd.DataFrame:
    assets = pd.read_csv(path)
    missing = set(ASSET_COLUMNS) - set(assets.columns)
    if missing:
        raise ValueError(f"assets.csv is missing: {sorted(missing)}")
    assets = assets.loc[:, ASSET_COLUMNS].copy()
    assets["asset"] = assets["asset"].astype(str).str.strip()
    if assets["asset"].duplicated().any() or assets["asset"].eq("").any():
        raise ValueError("asset names must be non-empty and unique")
    numeric = assets.loc[:, ASSET_COLUMNS[1:]].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("asset assumptions must be finite")
    assets.loc[:, ASSET_COLUMNS[1:]] = numeric
    if (assets["volatility"] < 0).any() or (assets["tax_drag"] < 0).any():
        raise ValueError("volatility and tax_drag cannot be negative")
    return assets


def _load_correlation(path: Path, names: list[str]) -> np.ndarray:
    frame = pd.read_csv(path, index_col=0)
    if set(frame.index) != set(names) or set(frame.columns) != set(names):
        raise ValueError("correlations.csv must contain the same assets on both axes")
    correlation = frame.loc[names, names].to_numpy(dtype=float)
    if not np.isfinite(correlation).all():
        raise ValueError("correlations must be finite")
    if not np.allclose(correlation, correlation.T, atol=1e-10):
        raise ValueError("correlation matrix must be symmetric")
    if not np.allclose(np.diag(correlation), 1.0, atol=1e-10):
        raise ValueError("correlation diagonal must equal one")
    if np.linalg.eigvalsh(correlation).min() < -1e-8:
        raise ValueError("correlation matrix must be positive semidefinite")
    return correlation


def _load_portfolios(path: Path, names: list[str]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    frame = pd.read_csv(path)
    missing = set(PORTFOLIO_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"portfolios.csv is missing: {sorted(missing)}")
    frame = frame.loc[:, PORTFOLIO_COLUMNS].copy()
    frame["weight"] = pd.to_numeric(frame["weight"], errors="raise")
    if (frame["weight"] < -1e-12).any():
        raise ValueError("this public engine does not support short weights")
    if not set(frame["account"]).issubset(ACCOUNTS):
        raise ValueError(f"account must be one of {ACCOUNTS}")
    if not set(frame["asset"]).issubset(names):
        raise ValueError("portfolios.csv contains unknown assets")
    portfolios = {}
    for strategy, strategy_rows in frame.groupby("strategy", sort=True):
        weights = []
        for account in ACCOUNTS:
            rows = strategy_rows.loc[strategy_rows["account"].eq(account)]
            if rows["asset"].duplicated().any():
                raise ValueError(f"duplicate asset weights for {strategy}/{account}")
            vector = rows.set_index("asset")["weight"].reindex(names, fill_value=0.0)
            if not np.isclose(vector.sum(), 1.0, atol=1e-8):
                raise ValueError(f"weights for {strategy}/{account} must sum to one")
            weights.append(vector.to_numpy(dtype=float))
        portfolios[str(strategy)] = (weights[0], weights[1])
    if len(portfolios) < 2:
        raise ValueError("at least two strategies are required for comparison")
    return portfolios


def load_research_bundle(input_dir: Path) -> ResearchBundle:
    """Load four documented files without supplying or inferring research data."""
    required = {"assumptions.json", "assets.csv", "correlations.csv", "portfolios.csv"}
    missing = [name for name in sorted(required) if not (input_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"input bundle is missing: {missing}")
    config = _load_config(input_dir / "assumptions.json")
    assets = _load_assets(input_dir / "assets.csv")
    names = assets["asset"].tolist()
    correlation = _load_correlation(input_dir / "correlations.csv", names)
    portfolios = _load_portfolios(input_dir / "portfolios.csv", names)
    return ResearchBundle(config, assets, correlation, portfolios)

