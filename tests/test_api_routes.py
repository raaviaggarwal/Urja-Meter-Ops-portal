"""Maintained API route tests migrated from the obsolete tests.py script."""

import math

from fastapi.testclient import TestClient

import app as app_module
from app import TOTAL_RECORDS, app, dataset

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_default_listing() -> None:
    response = client.get("/api/meters")
    assert response.status_code == 200
    body = response.json()
    assert "meters" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "total_pages" in body
    assert body["total"] == TOTAL_RECORDS
    assert len(body["meters"]) <= body["per_page"]


def test_pagination_page_one() -> None:
    response = client.get("/api/meters?page=1&per_page=5")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 5
    assert len(body["meters"]) <= 5


def test_pagination_page_two() -> None:
    response = client.get("/api/meters?page=2&per_page=5")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2


def test_pagination_beyond_data() -> None:
    response = client.get("/api/meters?page=999&per_page=5")
    assert response.status_code == 200
    body = response.json()
    assert body["meters"] == []
    assert body["total"] == TOTAL_RECORDS


def test_search_by_meter_id() -> None:
    meter_id = dataset[0]["meterId"]
    response = client.get(f"/api/meters/search?query={meter_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(meter["meterId"] == meter_id for meter in body["meters"])


def test_search_by_serial() -> None:
    serial = dataset[0]["serialNo"]
    response = client.get(f"/api/meters/search?query={serial}")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(meter["serialNo"] == serial for meter in body["meters"])


def test_search_no_results() -> None:
    response = client.get("/api/meters/search?query=nonexistentmeter")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["meters"] == []


def test_search_empty_string() -> None:
    response = client.get("/api/meters/search?query=")
    assert response.status_code == 422


def test_status_installed() -> None:
    response = client.get("/api/meters/status/Installed")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Installed"
    assert body["total"] > 0
    for meter in body["meters"]:
        assert meter["installStatus"] == "Installed"


def test_status_faulty() -> None:
    response = client.get("/api/meters/status/Faulty")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Faulty"
    for meter in body["meters"]:
        assert meter["installStatus"] == "Faulty"


def test_status_decommissioned() -> None:
    response = client.get("/api/meters/status/Decommissioned")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Decommissioned"
    for meter in body["meters"]:
        assert meter["installStatus"] == "Decommissioned"


def test_get_existing_meter() -> None:
    meter_id = dataset[0]["meterId"]
    response = client.get(f"/api/meters/{meter_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["meterId"] == meter_id
    assert "installStatus" in body


def test_get_nonexistent_meter() -> None:
    response = client.get("/api/meters/nonexistent-id-12345")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_transformers_endpoint() -> None:
    response = client.get("/api/transformers")
    assert response.status_code == 200
    body = response.json()
    assert "transformers" in body
    assert "total" in body
    assert body["total"] > 0


def test_export_meters() -> None:
    response = client.get("/api/export/meters")
    assert response.status_code == 200
    body = response.json()
    assert "count" in body
    assert "meters" in body
    assert body["count"] == TOTAL_RECORDS
    assert len(body["meters"]) == TOTAL_RECORDS


def test_nearby_meters_calculates_distance_and_applies_radius(
    monkeypatch,
) -> None:
    origin = {**dataset[0], "geo": {"lat": 0.0, "lng": 0.0}}
    nearby = {**dataset[1], "geo": {"lat": 0.0, "lng": 0.01}}
    outside = {**dataset[2], "geo": {"lat": 0.0, "lng": 0.1}}
    monkeypatch.setattr(app_module, "dataset", [origin, nearby, outside])

    response = client.get(
        "/api/meters/nearby",
        params={"latitude": 0, "longitude": 0, "radius_km": 1.2},
    )

    assert response.status_code == 200
    body = response.json()
    assert [meter["meterId"] for meter in body["meters"]] == [
        origin["meterId"],
        nearby["meterId"],
    ]
    assert body["meters"][0]["distance_km"] == 0
    expected_distance = 6371 * math.radians(0.01)
    assert body["meters"][1]["distance_km"] == round(expected_distance, 4)


def test_hierarchy_reconstructs_and_filters_synthetic_records() -> None:
    record = dataset[0]
    hierarchy = record["hierarchy"]

    response = client.get("/api/hierarchy")

    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == len(dataset)
    zone = body["zones"][hierarchy["zone"]["name"]]
    circle = zone["circles"][hierarchy["circle"]["name"]]
    division = circle["divisions"][hierarchy["division"]["name"]]
    subdivision = division["subdivisions"][hierarchy["subdivision"]["name"]]
    substation = subdivision["substations"][hierarchy["substation"]["name"]]
    feeder = substation["feeders"][hierarchy["feeder"]["name"]]
    transformer = feeder["dts"][hierarchy["dt"]["name"]]
    path_levels = (
        "zone",
        "circle",
        "division",
        "subdivision",
        "substation",
        "feeder",
        "dt",
    )
    expected_meter_ids = [
        item["meterId"]
        for item in dataset
        if all(
            item["hierarchy"][level]["code"] == hierarchy[level]["code"]
            for level in path_levels
        )
    ]
    assert transformer["code"] == hierarchy["dt"]["code"]
    assert transformer["meterCount"] == len(expected_meter_ids)
    assert transformer["meterIds"] == expected_meter_ids[:20]

    filtered_response = client.get(
        "/api/hierarchy",
        params={"zone_code": hierarchy["zone"]["code"]},
    )

    assert filtered_response.status_code == 200
    filtered_body = filtered_response.json()
    assert filtered_body["total_records"] == len(dataset)
    assert list(filtered_body["zones"]) == [hierarchy["zone"]["name"]]


def test_query_meters_combines_synthetic_filters_with_and() -> None:
    sample = dataset[0]
    hierarchy = sample["hierarchy"]
    params = {
        "status": sample["installStatus"],
        "make": sample["make"],
        "phase_type": sample["phaseType"],
        "install_type": sample["installType"],
        "dt_code": sample["dtCode"],
        "zone_code": hierarchy["zone"]["code"],
        "circle_code": hierarchy["circle"]["code"],
        "feeder_code": hierarchy["feeder"]["code"],
        "per_page": 100,
    }
    expected_ids = {
        record["meterId"]
        for record in dataset
        if record["installStatus"] == params["status"]
        and record["make"] == params["make"]
        and record["phaseType"] == params["phase_type"]
        and record["installType"] == params["install_type"]
        and record["dtCode"] == params["dt_code"]
        and record["hierarchy"]["zone"]["code"] == params["zone_code"]
        and record["hierarchy"]["circle"]["code"] == params["circle_code"]
        and record["hierarchy"]["feeder"]["code"] == params["feeder_code"]
    }

    response = client.get("/api/meters/query", params=params)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == len(expected_ids)
    assert {record["meterId"] for record in body["meters"]} == expected_ids
    assert body["total_pages"] == 1


def test_nonexistent_meter_returns_404() -> None:
    response = client.get("/api/meters/absolutely-nonexistent")
    assert response.status_code == 404
