"""Command-line entry point for the public household research engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from .engine import simulate
from .inputs import load_research_bundle
from .reporting import save_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    bundle = load_research_bundle(args.input_dir)
    yearly, terminal = simulate(bundle)
    summary = save_outputs(yearly, terminal, args.output, bundle.config)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

