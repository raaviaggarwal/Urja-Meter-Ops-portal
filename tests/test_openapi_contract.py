import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import MeterRecord, app, dataset


client = TestClient(app)


def test_checked_in_openapi_matches_runtime_schema() -> None:
    openapi_path = Path(__file__).parents[1] / "openapi.json"
    checked_in_schema = json.loads(openapi_path.read_text(encoding="utf-8"))

    assert checked_in_schema == app.openapi()


def test_openapi_documents_bounds_and_runtime_error_responses() -> None:
    schema = app.openapi()
    nearby = schema["paths"]["/api/meters/nearby"]["get"]
    parameters = {parameter["name"]: parameter for parameter in nearby["parameters"]}

    assert parameters["latitude"]["schema"]["minimum"] == -90
    assert parameters["latitude"]["schema"]["maximum"] == 90
    assert parameters["longitude"]["schema"]["minimum"] == -180
    assert parameters["longitude"]["schema"]["maximum"] == 180
    assert "400" in nearby["responses"]
    api_error = "#/components/schemas/APIErrorResponse"
    assert (
        nearby["responses"]["400"]["content"]["application/json"]["schema"]["$ref"]
        == api_error
    )
    for path in ("/api/hierarchy", "/api/meters/{meter_id}"):
        response = schema["paths"][path]["get"]["responses"]["404"]
        assert response["content"]["application/json"]["schema"]["$ref"] == api_error

    for path_items in schema["paths"].values():
        for operation in path_items.values():
            assert "500" in operation["responses"]
            server_error_ref = operation["responses"]["500"]["content"][
                "application/json"
            ]["schema"]["$ref"]
            assert server_error_ref == (
                "#/components/schemas/InternalErrorResponse"
            )

    response_models = {
        "/api/meters": "PaginatedMeterSummaries",
        "/api/meters/search": "MeterSearchResults",
        "/api/meters/status/{status}": "MetersByStatus",
        "/api/meters/query": "PaginatedMeterSummaries",
        "/api/meters/nearby": "NearbyMeters",
        "/api/hierarchy": "MeterHierarchyTree",
        "/api/transformers": "TransformerSummaries",
        "/api/export/meters": "MeterExport",
        "/api/metadata": "MeterDatasetMetadata",
        "/api/meters/{meter_id}": "MeterRecord",
    }
    for path, model in response_models.items():
        response_schema = schema["paths"][path]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        assert response_schema["$ref"] == f"#/components/schemas/{model}"


def test_typed_responses_preserve_existing_json_shapes_and_extra_fields() -> None:
    record = dataset[0]
    summary = client.get(
        "/api/meters",
        params={"search": record["meterId"]},
    ).json()["meters"][0]
    detail = client.get(f"/api/meters/{record['meterId']}").json()

    assert set(summary) == {
        "meterId",
        "serialNo",
        "make",
        "phaseType",
        "installStatus",
        "dtCode",
        "hierarchy",
        "geo",
    }
    assert detail == record

    extended_record = {**record, "syntheticExtension": {"preserved": True}}
    serialized = MeterRecord.model_validate(extended_record).model_dump(
        by_alias=True
    )
    assert serialized["syntheticExtension"] == {"preserved": True}


def test_documented_custom_errors_match_runtime_responses() -> None:
    nearby = client.get(
        "/api/meters/nearby",
        params={"latitude": 91, "longitude": 0, "radius_km": 5},
    )
    missing_meter = client.get("/api/meters/not-in-synthetic-fixture")
    missing_zone = client.get("/api/hierarchy", params={"zone_code": "Z-UNKNOWN"})

    assert nearby.status_code == 400
    assert nearby.json() == {
        "error": "Latitude must be between -90 and 90",
        "message": "Latitude must be between -90 and 90",
        "detail": "Latitude must be between -90 and 90",
    }
    assert missing_meter.status_code == 404
    assert missing_meter.json() == {
        "error": "Meter not found",
        "message": "Meter not found",
        "detail": "Meter not found",
    }
    assert missing_zone.status_code == 404
    assert missing_zone.json() == {
        "error": "Zone with code 'Z-UNKNOWN' not found",
        "message": "Zone with code 'Z-UNKNOWN' not found",
        "detail": "Zone with code 'Z-UNKNOWN' not found",
    }
