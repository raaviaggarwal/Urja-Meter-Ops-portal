"""Automated tests for the Fluck Energy Meter API."""

import json
import pytest
from fastapi.testclient import TestClient
from app import app, dataset, TOTAL_RECORDS

client = TestClient(app)


class TestHealth:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestListingDefault:
    def test_default_listing(self):
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


class TestPagination:
    def test_pagination_page_one(self):
        response = client.get("/api/meters?page=1&per_page=5")
        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 1
        assert body["per_page"] == 5
        assert len(body["meters"]) <= 5

    def test_pagination_page_two(self):
        response = client.get("/api/meters?page=2&per_page=5")
        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 2

    def test_pagination_beyond_data(self):
        response = client.get("/api/meters?page=999&per_page=5")
        assert response.status_code == 200
        body = response.json()
        assert body["meters"] == []
        assert body["total"] == TOTAL_RECORDS


class TestSearch:
    def test_search_by_meter_id(self):
        # Use the first meter's ID from the dataset
        meter_id = dataset[0]["meterId"]
        response = client.get(f"/api/meters/search?query={meter_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert any(m["meterId"] == meter_id for m in body["meters"])

    def test_search_by_serial(self):
        serial = dataset[0]["serialNo"]
        response = client.get(f"/api/meters/search?query={serial}")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert any(m["serialNo"] == serial for m in body["meters"])

    def test_search_no_results(self):
        response = client.get("/api/meters/search?query=nonexistentmeter")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 0
        assert body["meters"] == []

    def test_search_empty_string(self):
        # FastAPI will reject empty strings since min_length=1 in the schema
        response = client.get("/api/meters/search?query=")
        assert response.status_code == 422  # validation error


class TestStatusFilter:
    def test_status_installed(self):
        response = client.get("/api/meters/status/Installed")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "Installed"
        assert body["total"] > 0
        # Verify all returned meters have the correct status
        for m in body["meters"]:
            assert m["installStatus"] == "Installed"

    def test_status_faulty(self):
        response = client.get("/api/meters/status/Faulty")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "Faulty"
        for m in body["meters"]:
            assert m["installStatus"] == "Faulty"

    def test_status_decommissioned(self):
        response = client.get("/api/meters/status/Decommissioned")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "Decommissioned"
        for m in body["meters"]:
            assert m["installStatus"] == "Decommissioned"


class TestIndividualMeter:
    def test_get_existing_meter(self):
        meter_id = dataset[0]["meterId"]
        response = client.get(f"/api/meters/{meter_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["meterId"] == meter_id
        assert "installStatus" in body

    def test_get_nonexistent_meter(self):
        response = client.get("/api/meters/nonexistent-id-12345")
        assert response.status_code == 404
        assert "detail" in response.json()


class TestTransformers:
    def test_transformers_endpoint(self):
        response = client.get("/api/transformers")
        assert response.status_code == 200
        body = response.json()
        assert "transformers" in body
        assert "total" in body
        assert body["total"] > 0


class TestExport:
    def test_export_meters(self):
        response = client.get("/api/export/meters")
        assert response.status_code == 200
        body = response.json()
        assert "count" in body
        assert "meters" in body
        assert body["count"] == TOTAL_RECORDS
        assert len(body["meters"]) == TOTAL_RECORDS


class TestMissingMeter:
    def test_nonexistent_meter_returns_404(self):
        response = client.get("/api/meters/ absolutely-nonexistent")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Helper: module-level setup (import-time) so TOTAL_RECORDS is available
# ---------------------------------------------------------------------------
# The tests import `dataset` and `TOTAL_RECORDS` from `app`; those are populated
# at module load time by the `load_dataset()` call at the top of `app.py`.
# If the dataset file is missing, the app will still start but TOTAL_RECORDS
# will be 0 and dataset []. The tests will still run (just with empty data).
# ---------------------------------------------------------------------------

# Run these with: pytest tests.py -v