import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.engine import simulate
from src.inputs import load_research_bundle
from src.reporting import save_outputs


def write_test_bundle(root: Path) -> None:
    (root / "assumptions.json").write_text(json.dumps({
        "years": 3, "simulations": 25, "seed": 7,
        "initial_wealth": 1_000_000, "tax_deferred_share": 0.5,
    }), encoding="utf-8")
    pd.DataFrame({
        "asset": ["Asset A", "Asset B", "Asset C"],
        "expected_return": [0.07, 0.04, 0.03],
        "volatility": [0.16, 0.07, 0.09],
        "tax_drag": [0.004, 0.012, 0.006],
    }).to_csv(root / "assets.csv", index=False)
    names = ["Asset A", "Asset B", "Asset C"]
    pd.DataFrame(
        [[1.0, 0.2, 0.0], [0.2, 1.0, 0.1], [0.0, 0.1, 1.0]],
        index=names, columns=names,
    ).to_csv(root / "correlations.csv")
    rows = []
    weights = {
        "Baseline": ([0.6, 0.3, 0.1], [0.6, 0.3, 0.1]),
        "Research": ([0.3, 0.6, 0.1], [0.9, 0.0, 0.1]),
    }
    for strategy, (deferred, taxable) in weights.items():
        for account, vector in (("tax_deferred", deferred), ("taxable", taxable)):
            rows.extend({
                "strategy": strategy, "account": account,
                "asset": asset, "weight": weight,
            } for asset, weight in zip(names, vector))
    pd.DataFrame(rows).to_csv(root / "portfolios.csv", index=False)


def test_engine_is_reproducible(tmp_path: Path) -> None:
    write_test_bundle(tmp_path)
    bundle = load_research_bundle(tmp_path)
    first, second = simulate(bundle), simulate(bundle)
    assert first[0].equals(second[0])
    assert first[1].equals(second[1])


def test_paired_paths_preserve_equal_household_exposure(tmp_path: Path) -> None:
    write_test_bundle(tmp_path)
    portfolios = load_research_bundle(tmp_path).portfolios
    for strategy in ("Baseline", "Research"):
        deferred, taxable = portfolios[strategy]
        assert np.allclose(0.5 * deferred + 0.5 * taxable, [0.6, 0.3, 0.1])


def test_reporting_writes_dashboard_without_publishing_inputs(tmp_path: Path) -> None:
    inputs, outputs = tmp_path / "private-inputs", tmp_path / "outputs"
    inputs.mkdir()
    write_test_bundle(inputs)
    bundle = load_research_bundle(inputs)
    yearly, terminal = simulate(bundle)
    summary = save_outputs(yearly, terminal, outputs, bundle.config)
    assert set(summary["strategy"]) == {"Baseline", "Research"}
    for name in ("summary.csv", "wealth_quantiles.csv", "run_manifest.csv", "path_dashboard.html"):
        assert (outputs / name).is_file()

