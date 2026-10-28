"""Synthetic-only tests for the meter ingestion pipeline."""

import json
from pathlib import Path

import pytest

from ingest_meters import main
from meter_ingestion import (
    IngestionInputError,
    read_input,
    validate_records,
    write_output_atomic,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_FIXTURE = (
    REPOSITORY_ROOT / "tests" / "fixtures" / "meter-export.synthetic.json"
)


def _synthetic_record() -> dict:
    return json.loads(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))[0]


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_valid_synthetic_input_is_valid_and_written_atomically(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    destination = tmp_path / "output.json"
    record = _synthetic_record()
    _write_json(source, [record])

    records = read_input(source)
    report = validate_records(records)
    assert report.is_valid
    assert report.total_records == 1
    assert report.valid_records == 1
    assert report.invalid_records == 0
    assert report.duplicate_ids == 0

    write_output_atomic(records, destination, source)
    assert json.loads(destination.read_text(encoding="utf-8")) == [record]
    assert not list(tmp_path.glob(".output.json.*.tmp"))


def test_empty_array_is_valid_and_written(tmp_path: Path) -> None:
    source = tmp_path / "empty.json"
    destination = tmp_path / "output.json"
    _write_json(source, [])

    report = validate_records(read_input(source))
    assert report.is_valid
    assert (report.total_records, report.valid_records, report.invalid_records) == (
        0,
        0,
        0,
    )
    write_output_atomic([], destination, source)
    assert json.loads(destination.read_text(encoding="utf-8")) == []


def test_invalid_json_has_location_without_echoing_content(tmp_path: Path) -> None:
    source = tmp_path / "invalid.json"
    source.write_text('{"sensitive-looking-content":', encoding="utf-8")

    with pytest.raises(IngestionInputError, match=r"line 1, column"):
        read_input(source)


def test_invalid_utf8_is_reported_without_echoing_input(tmp_path: Path) -> None:
    source = tmp_path / "invalid-encoding.json"
    source.write_bytes(bytes((ord("["), ord('"'), 0xFF, ord('"'), ord("]"))))

    with pytest.raises(IngestionInputError, match="not valid UTF-8"):
        read_input(source)


@pytest.mark.parametrize("top_level", [{"records": []}, "not-an-array", None, 1])
def test_wrong_top_level_type_is_rejected(
    tmp_path: Path, top_level: object
) -> None:
    source = tmp_path / "input.json"
    _write_json(source, top_level)

    with pytest.raises(IngestionInputError, match="must be an array"):
        read_input(source)


def test_missing_required_identifier_is_invalid() -> None:
    record = _synthetic_record()
    del record["meterId"]

    report = validate_records([record])
    assert not report.is_valid
    assert report.invalid_records == 1
    assert any("'meterId'" in error for error in report.errors)
    assert any("missing required field 'meterId'" in error for error in report.errors)


def test_duplicate_ids_are_reported_without_revealing_the_identifier() -> None:
    record = _synthetic_record()
    report = validate_records([record, record.copy()])

    assert not report.is_valid
    assert report.total_records == 2
    assert report.valid_records == 1
    assert report.invalid_records == 1
    assert report.duplicate_ids == 1
    assert any("duplicates record 1" in error for error in report.errors)
    assert record["meterId"] not in " ".join(report.errors)


def test_additional_fields_are_preserved_and_reported_as_warnings() -> None:
    record = _synthetic_record()
    record["extraField"] = "synthetic-only"

    report = validate_records([record])
    assert report.is_valid
    assert len(report.warnings) == 1
    assert "record 1: additional fields present" == report.warnings[0]


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("hierarchy", [], "'hierarchy' must be an object"),
        ("geo", [], "'geo' must be an object"),
    ],
)
def test_malformed_nested_objects_are_invalid(
    field: str, value: object, expected_error: str
) -> None:
    record = _synthetic_record()
    record[field] = value

    report = validate_records([record])
    assert not report.is_valid
    assert report.invalid_records == 1
    assert any(expected_error in error for error in report.errors)


def test_malformed_hierarchy_level_and_geographic_coordinate_are_invalid() -> None:
    record = _synthetic_record()
    record["hierarchy"]["zone"] = "not-an-object"
    record["geo"]["lat"] = "not-a-number"

    report = validate_records([record])
    assert not report.is_valid
    assert any("'hierarchy.zone' must be an object" in error for error in report.errors)
    assert any("'geo.lat' must be a finite number" in error for error in report.errors)


def test_existing_destination_is_replaced_after_successful_validation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "input.json"
    destination = tmp_path / "output.json"
    record = _synthetic_record()
    _write_json(source, [record])
    destination.write_text("old output", encoding="utf-8")

    write_output_atomic(read_input(source), destination, source)
    assert json.loads(destination.read_text(encoding="utf-8")) == [record]


def test_input_and_output_cannot_be_the_same_path(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    _write_json(source, [_synthetic_record()])
    original = source.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="must be different"):
        write_output_atomic(read_input(source), source, source)
    assert source.read_text(encoding="utf-8") == original


def test_validation_failure_leaves_existing_destination_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "input.json"
    destination = tmp_path / "output.json"
    record = _synthetic_record()
    del record["meterId"]
    _write_json(source, [record])
    destination.write_text("existing output", encoding="utf-8")

    result = main([str(source), "--output", str(destination)])
    output = capsys.readouterr()

    assert result == 1
    assert "invalid=1" in output.out
    assert "meterId" in output.err
    assert destination.read_text(encoding="utf-8") == "existing output"


def test_cli_requires_explicit_output_and_reports_counts_without_record_values(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "input.json"
    destination = tmp_path / "output.json"
    record = _synthetic_record()
    record["geo"]["lat"] = "invalid"
    _write_json(source, [record])

    result = main([str(source), "--output", str(destination)])
    output = capsys.readouterr()

    assert result == 1
    assert "total=1 valid=0 invalid=1 duplicate_ids=0" in output.out
    assert "'geo.lat'" in output.err
    assert record["meterId"] not in output.out + output.err
    assert not destination.exists()


def test_cli_rejects_input_path_as_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "input.json"
    _write_json(source, [_synthetic_record()])
    original = source.read_text(encoding="utf-8")

    result = main([str(source), "--output", str(source)])
    output = capsys.readouterr()

    assert result == 2
    assert "paths must be different" in output.err
    assert source.read_text(encoding="utf-8") == original
