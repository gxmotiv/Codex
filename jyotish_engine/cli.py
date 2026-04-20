from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import compute_chart


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Jyotish Engine Prototype")
    parser.add_argument("input", type=Path, help="Path to chart request JSON")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())
    result = compute_chart(payload)
    output = json.dumps(result, indent=2)

    if args.output:
        args.output.write_text(output + "\n")
    else:
        print(output)


if __name__ == "__main__":
    main()
