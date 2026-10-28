"""Validation and atomic writing helpers for local meter export files."""

from __future__ import annotations

import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STRING_FIELDS = (
    "serialNo",
    "make",
    "phaseType",
    "installStatus",
    "installType",
    "build",
    "dtCode",
)
HIERARCHY_LEVELS = (
    "zone",
    "circle",
    "division",
    "subdivision",
    "substation",
    "feeder",
    "dt",
)
REQUIRED_FIELDS = frozenset(
    {
        "meterId",
        *STRING_FIELDS,
        "hierarchy",
        "geo",
    }
)


class IngestionInputError(Exception):
    """Raised when an input file cannot be parsed as a JSON array."""


@dataclass(frozen=True)
class ValidationReport:
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_ids: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.invalid_records == 0


def read_input(path: Path) -> list[Any]:
    """Read a JSON array without including record contents in errors."""
    try:
        with path.open("r", encoding="utf-8") as source:
            data = json.load(source)
    except json.JSONDecodeError as exc:
        raise IngestionInputError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}"
        ) from None
    except UnicodeDecodeError:
        raise IngestionInputError("input file is not valid UTF-8") from None
    except OSError as exc:
        raise IngestionInputError(
            f"unable to read input file ({type(exc).__name__})"
        ) from None

    if not isinstance(data, list):
        raise IngestionInputError("top-level JSON value must be an array")
    return data


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_records(records: list[Any]) -> ValidationReport:
    """Validate API-compatible records and report issues without data values."""
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: dict[str, int] = {}
    invalid_records = 0
    duplicate_ids = 0

    for index, record in enumerate(records, start=1):
        record_errors: list[str] = []
        if not isinstance(record, dict):
            errors.append(f"record {index}: expected an object")
            invalid_records += 1
            continue

        for field in sorted(REQUIRED_FIELDS - record.keys()):
            record_errors.append(f"missing required field '{field}'")

        meter_id = record.get("meterId")
        if not isinstance(meter_id, str) or not meter_id.strip():
            record_errors.append("'meterId' must be a non-empty string")
        else:
            previous_index = seen_ids.get(meter_id)
            if previous_index is not None:
                record_errors.append(
                    f"'meterId' duplicates record {previous_index}"
                )
                duplicate_ids += 1
            else:
                seen_ids[meter_id] = index

        for field in STRING_FIELDS:
            if field in record and not isinstance(record[field], str):
                record_errors.append(f"'{field}' must be a string")

        hierarchy = record.get("hierarchy")
        if "hierarchy" in record:
            if not isinstance(hierarchy, dict):
                record_errors.append("'hierarchy' must be an object")
            else:
                for level in HIERARCHY_LEVELS:
                    level_value = hierarchy.get(level)
                    if level not in hierarchy:
                        record_errors.append(
                            f"'hierarchy.{level}' is required"
                        )
                    elif not isinstance(level_value, dict):
                        record_errors.append(
                            f"'hierarchy.{level}' must be an object"
                        )
                    else:
                        for attribute in ("name", "code"):
                            value = level_value.get(attribute)
                            if not isinstance(value, str):
                                record_errors.append(
                                    f"'hierarchy.{level}.{attribute}' "
                                    "must be a string"
                                )
                extra_levels = sorted(set(hierarchy) - set(HIERARCHY_LEVELS))
                if extra_levels:
                    warnings.append(
                        f"record {index}: additional hierarchy fields present"
                    )

        geo = record.get("geo")
        if "geo" in record:
            if not isinstance(geo, dict):
                record_errors.append("'geo' must be an object")
            else:
                for coordinate, minimum, maximum in (
                    ("lat", -90, 90),
                    ("lng", -180, 180),
                ):
                    value = geo.get(coordinate)
                    if not _is_number(value) or (
                        isinstance(value, float) and not math.isfinite(value)
                    ):
                        record_errors.append(
                            f"'geo.{coordinate}' must be a finite number"
                        )
                    elif not minimum <= value <= maximum:
                        record_errors.append(
                            f"'geo.{coordinate}' is outside its valid range"
                        )
                extra_coordinates = sorted(set(geo) - {"lat", "lng"})
                if extra_coordinates:
                    warnings.append(
                        f"record {index}: additional geographic fields present"
                    )

        extra_fields = sorted(set(record) - REQUIRED_FIELDS)
        if extra_fields:
            warnings.append(f"record {index}: additional fields present")

        if record_errors:
            invalid_records += 1
            errors.extend(
                f"record {index}: {message}" for message in record_errors
            )

    return ValidationReport(
        total_records=len(records),
        valid_records=len(records) - invalid_records,
        invalid_records=invalid_records,
        duplicate_ids=duplicate_ids,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _same_file(input_path: Path, output_path: Path) -> bool:
    if input_path.resolve() == output_path.resolve():
        return True
    try:
        return os.path.samefile(input_path, output_path)
    except (FileNotFoundError, OSError):
        return False


def write_output_atomic(
    records: list[Any],
    output_path: Path,
    input_path: Path,
) -> None:
    """Write validated records using a same-directory atomic replacement."""
    if _same_file(input_path, output_path):
        raise ValueError("input and output paths must be different")
    if not validate_records(records).is_valid:
        raise ValueError("records failed validation")

    parent = output_path.parent
    if not parent.is_dir():
        raise OSError("output directory does not exist")
    if output_path.exists() and output_path.is_dir():
        raise OSError("output destination is a directory")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(records, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
