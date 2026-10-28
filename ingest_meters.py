"""Command-line interface for validating and importing meter JSON files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from meter_ingestion import (
    IngestionInputError,
    read_input,
    validate_records,
    write_output_atomic,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local meter JSON array and write it to an explicit "
            "destination."
        )
    )
    parser.add_argument("input", type=Path, help="input JSON array path")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="destination JSON path (replaced only after successful validation)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        records = read_input(args.input)
    except IngestionInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = validate_records(records)
    print(
        "records: "
        f"total={report.total_records} "
        f"valid={report.valid_records} "
        f"invalid={report.invalid_records} "
        f"duplicate_ids={report.duplicate_ids} "
        f"warnings={len(report.warnings)}"
    )
    for warning in report.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if not report.is_valid:
        for error in report.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    try:
        write_output_atomic(records, args.output, args.input)
    except (OSError, ValueError) as exc:
        print(
            f"error: unable to write output ({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return 2

    print("output: written atomically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
