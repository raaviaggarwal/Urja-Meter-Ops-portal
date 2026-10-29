"""Maintained API route tests migrated from the obsolete tests.py script."""

from fastapi.testclient import TestClient

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


def test_nonexistent_meter_returns_404() -> None:
    response = client.get("/api/meters/absolutely-nonexistent")
    assert response.status_code == 404
