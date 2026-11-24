"""Typed research inputs shared by validation and simulation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimulationConfig:
    years: int
    simulations: int
    seed: int
    initial_wealth: float
    tax_deferred_share: float


@dataclass(frozen=True)
class ResearchBundle:
    config: SimulationConfig
    assets: pd.DataFrame
    correlation: np.ndarray
    portfolios: dict[str, tuple[np.ndarray, np.ndarray]]

