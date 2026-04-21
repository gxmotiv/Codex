from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import compute_chart
from .interpretation import interpret_chart


def _add_output_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path")


def _emit(output_obj: dict, output_path: Path | None) -> None:
    serialized = json.dumps(output_obj, indent=2)
    if output_path:
        output_path.write_text(serialized + "\n")
        return
    print(serialized)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Jyotish Engine Prototype")
    sub = parser.add_subparsers(dest="command", required=True)

    chart_parser = sub.add_parser("chart", help="Compute raw chart from request JSON")
    chart_parser.add_argument("input", type=Path, help="Path to chart request JSON")
    _add_output_arg(chart_parser)

    interpret_parser = sub.add_parser("interpret", help="Compute chart and interpretation from request JSON")
    interpret_parser.add_argument("input", type=Path, help="Path to chart request JSON")
    _add_output_arg(interpret_parser)

    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    chart = compute_chart(payload)

    if args.command == "chart":
        _emit(chart, args.output)
        return

    result = {
        "chart": chart,
        "interpretation": interpret_chart(chart),
    }
    _emit(result, args.output)


if __name__ == "__main__":
    main()
