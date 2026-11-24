"""Research summaries and a standalone path dashboard."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .models import SimulationConfig


def _rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    red, green, blue = (int(value[index:index + 2], 16) for index in (0, 2, 4))
    return f"rgba({red},{green},{blue},{alpha})"


def summarize(terminal: pd.DataFrame) -> pd.DataFrame:
    return terminal.groupby("strategy").agg(
        p10_terminal_wealth=("terminal_wealth", lambda s: s.quantile(0.10)),
        median_terminal_wealth=("terminal_wealth", "median"),
        p90_terminal_wealth=("terminal_wealth", lambda s: s.quantile(0.90)),
        mean_cumulative_tax_drag=("cumulative_tax_drag", "mean"),
    ).reset_index()


def build_path_dashboard(yearly: pd.DataFrame, output_file: Path) -> None:
    quantiles = yearly.groupby(["strategy", "year"])["household_wealth"].quantile(
        [0.10, 0.50, 0.90]
    ).unstack().rename(columns={0.10: "p10", 0.50: "median", 0.90: "p90"}).reset_index()
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "Household wealth distribution", "Median cumulative tax drag"
    ))
    palette = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]
    for color, (strategy, group) in zip(palette, quantiles.groupby("strategy")):
        fig.add_trace(go.Scatter(
            x=list(group["year"]) + list(group["year"])[::-1],
            y=list(group["p90"]) + list(group["p10"])[::-1],
            fill="toself", fillcolor=_rgba(color, 0.13),
            line={"color": "rgba(0,0,0,0)"}, hoverinfo="skip",
            name=f"{strategy} P10–P90",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=group["year"], y=group["median"],
            line={"color": color, "width": 3}, name=f"{strategy} median",
        ), row=1, col=1)
        drag = yearly.loc[yearly["strategy"].eq(strategy)].groupby(
            "year"
        )["cumulative_tax_drag"].median()
        fig.add_trace(go.Scatter(
            x=drag.index, y=drag.values,
            line={"color": color, "width": 3}, name=f"{strategy} tax drag",
        ), row=1, col=2)
    fig.update_layout(
        title="Household Research Path Dashboard", template="plotly_white",
        height=560, legend={"orientation": "h", "y": -0.18},
    )
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    fig.update_xaxes(title_text="Year")
    fig.write_html(output_file, include_plotlyjs=True, full_html=True)


def save_outputs(
    yearly: pd.DataFrame, terminal: pd.DataFrame, output: Path,
    config: SimulationConfig,
) -> pd.DataFrame:
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize(terminal)
    summary.to_csv(output / "summary.csv", index=False)
    quantiles = yearly.groupby(["strategy", "year"])["household_wealth"].quantile(
        [0.10, 0.50, 0.90]
    ).unstack().rename(columns={0.10: "p10", 0.50: "median", 0.90: "p90"}).reset_index()
    quantiles.to_csv(output / "wealth_quantiles.csv", index=False)
    pd.DataFrame([{
        "years": config.years, "simulations": config.simulations,
        "seed": config.seed, "initial_wealth": config.initial_wealth,
        "tax_deferred_share": config.tax_deferred_share,
    }]).to_csv(output / "run_manifest.csv", index=False)
    build_path_dashboard(yearly, output / "path_dashboard.html")
    return summary

