import numpy as np

from src.simulation import Config, simulate, strategy_weights, summarize


def test_household_exposure_is_preserved_at_equal_account_split() -> None:
    strategies = strategy_weights()
    expected = np.array([0.60, 0.30, 0.10])
    for deferred, taxable in strategies.values():
        assert np.allclose(0.5 * deferred + 0.5 * taxable, expected)
        assert np.isclose(deferred.sum(), 1.0)
        assert np.isclose(taxable.sum(), 1.0)


def test_simulation_is_reproducible() -> None:
    config = Config(years=3, simulations=20, seed=7)
    _, first = simulate(config)
    _, second = simulate(config)
    assert first.equals(second)


def test_summary_contains_both_strategies() -> None:
    _, terminal = simulate(Config(years=2, simulations=10))
    summary = summarize(terminal)
    assert set(summary["strategy"]) == {"Baseline", "Coordinated"}

