"""
cli.py — Entry point for Flint-X static analyzer.

Called by the Rust CLI as:
  python3 analyzer/cli.py --target <path> --output <json_path>

Prints JSON to stdout and optionally writes to a file.
"""

import argparse
import json
import os
import sys

# Allow imports from same directory
sys.path.insert(0, os.path.dirname(__file__))

from static_analyzer import analyze_file, analyze_directory


def main():
    parser = argparse.ArgumentParser(
        description="Flint-X Static Analyzer — AST-based Python performance analysis"
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to a Python file or directory to analyze",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write JSON output file",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    target = args.target

    if not os.path.exists(target):
        error = {"error": f"Target not found: {target}"}
        print(json.dumps(error, indent=2))
        sys.exit(1)

    if os.path.isdir(target):
        result = analyze_directory(target)
    else:
        result = analyze_file(target)

    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    # Always print to stdout (Rust CLI will capture this)
    print(output_json)

    # Optionally write to file
    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"\n[flintx] Analysis saved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()