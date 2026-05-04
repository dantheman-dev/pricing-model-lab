"""Command-line interface for the pricing model lab."""

from __future__ import annotations

import argparse
import sys

from pricing_model_lab.processor import DEFAULT_THRESHOLD, process


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pricing-model-lab",
        description=(
            "Compare observed vs. model values, compute deviations, "
            "and flag items that exceed a configurable threshold."
        ),
    )
    parser.add_argument(
        "input",
        metavar="INPUT_CSV",
        help="Path to the input CSV file (columns: item_id, observed_value, model_value).",
    )
    parser.add_argument(
        "output",
        metavar="OUTPUT_CSV",
        help="Path where the processed output CSV will be written.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        metavar="THRESHOLD",
        help=(
            "Absolute deviation threshold for the review flag "
            f"(default: {DEFAULT_THRESHOLD * 100:.0f}%%)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = process(args.input, args.output, threshold=args.threshold)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    flagged = result["review_flag"].sum()
    total = len(result)
    print(
        f"Processed {total} items. "
        f"{flagged} flagged (|deviation| > {args.threshold:.2%}). "
        f"Output written to: {args.output}"
    )


if __name__ == "__main__":
    main()
