import json
import os
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import load_dataset_snapshot


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "meter-export.synthetic.json"
)


def _write_synthetic_dataset(path: Path) -> list[dict]:
    records = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    path.write_text(json.dumps(records), encoding="utf-8")
    return records


def test_loads_valid_synthetic_dataset(tmp_path: Path) -> None:
    source = tmp_path / "meters.json"
    expected_records = _write_synthetic_dataset(source)

    records, modified_at = load_dataset_snapshot(str(source))

    assert records == expected_records
    assert modified_at == source.stat().st_mtime


def test_loads_empty_array(tmp_path: Path) -> None:
    source = tmp_path / "empty.json"
    source.write_text("[]", encoding="utf-8")

    records, _ = load_dataset_snapshot(str(source))

    assert records == []


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        ("{", "invalid JSON"),
        ('{"meterId": "synthetic"}', "must be an array"),
    ],
)
def test_rejects_unreadable_json_structure(
    tmp_path: Path, contents: str, message: str
) -> None:
    source = tmp_path / "invalid.json"
    source.write_text(contents, encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        load_dataset_snapshot(str(source))


def test_rejects_missing_dataset(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    with pytest.raises(RuntimeError, match="FileNotFoundError"):
        load_dataset_snapshot(str(missing))


def test_rejects_missing_identifier_without_record_values(
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing-id.json"
    records = _write_synthetic_dataset(source)
    records[0].pop("meterId")
    source.write_text(json.dumps(records), encoding="utf-8")

    with pytest.raises(
        RuntimeError,
        match="record 1: missing required field 'meterId'",
    ) as error:
        load_dataset_snapshot(str(source))

    assert "SYNTH-SERIAL-000001" not in str(error.value)


def test_rejects_duplicate_identifiers(tmp_path: Path) -> None:
    source = tmp_path / "duplicates.json"
    records = _write_synthetic_dataset(source)
    records[1]["meterId"] = records[0]["meterId"]
    source.write_text(json.dumps(records), encoding="utf-8")

    with pytest.raises(RuntimeError, match="meterId' duplicates record 1"):
        load_dataset_snapshot(str(source))


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("hierarchy", None, "'hierarchy' must be an object"),
        ("geo", {"lat": 1000, "lng": 0}, "'geo.lat' is outside its valid range"),
    ],
)
def test_rejects_malformed_nested_fields(
    tmp_path: Path, field: str, replacement: object, message: str
) -> None:
    source = tmp_path / "malformed-fields.json"
    records = _write_synthetic_dataset(source)
    records[0][field] = replacement
    source.write_text(json.dumps(records), encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        load_dataset_snapshot(str(source))


def test_metadata_reports_loaded_snapshot_timestamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "meters.json"
    _write_synthetic_dataset(source)
    _, loaded_mtime = load_dataset_snapshot(str(source))
    monkeypatch.setattr(app_module, "DATASET_FILE_MTIME", loaded_mtime)
    original_timestamp = datetime.fromtimestamp(loaded_mtime).isoformat()

    changed_mtime = loaded_mtime + 120
    os.utime(source, (changed_mtime, changed_mtime))
    response = TestClient(app_module.app).get("/api/metadata")

    assert response.status_code == 200
    assert response.json()["file_modification_time"] == original_timestamp


def test_metadata_returns_service_unavailable_when_dataset_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        app_module,
        "_dataset_load_error",
        "Dataset file not accessible (FileNotFoundError)",
    )
    monkeypatch.setattr(app_module, "DATASET_FILE_MTIME", None)

    response = TestClient(app_module.app).get("/api/metadata")

    assert response.status_code == 503
    assert response.json() == {
        "error": (
            "Meter dataset is unavailable; provide a valid "
            "meter-export.json and restart the service"
        ),
        "message": (
            "Meter dataset is unavailable; provide a valid "
            "meter-export.json and restart the service"
        ),
        "detail": (
            "Meter dataset is unavailable; provide a valid "
            "meter-export.json and restart the service"
        ),
    }
