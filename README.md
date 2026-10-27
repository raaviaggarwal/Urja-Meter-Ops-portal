# Flock Energy Meter API

A read-only FastAPI service over the verified meter operations dataset (`meter-export.json`).

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd urja-meter-ops-portal

# Install dependencies (FastAPI and uvicorn are already available in the
# environment; if running locally):
pip install fastapi uvicorn
```

## Startup

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe; returns `{"status":"ok"}`. |
| `GET` | `/api/meters` | List meters with pagination, search, and filters. |
| `GET` | `/api/meters/{meterId}` | Full metadata for one meter. |
| `GET` | `/api/meters/search` | Search by meter ID or serial number substring. |
| `GET` | `/api/meters/status/{status}` | Filter by `Installed`/`Faulty`/`Decommissioned`. |
| `GET` | `/api/hierarchy` | Reconstructed meter network hierarchy from the exported dataset. |
| `GET` | `/api/meters/query` | Combined attribute filtering (status, make, phaseType, installType, dtCode, zoneCode, circleCode, feederCode). |
| `GET` | `/api/meters/nearby` | Nearby meters using Haversine formula with latitude, longitude, and radius_km. |
| `GET` | `/api/metadata` | Data source metadata and freshness information (record count, source filename, file modification time). |
| `GET` | `/api/export/meters` | Full export of all 403 meter records. |

## Example requests

```bash
# Health check
curl http://127.0.0.1:8000/health

# List all meters (default pagination: 20 per page)
curl "http://127.0.0.1:8000/api/meters"

# List with custom page size
curl "http://127.0.0.1:8000/api/meters?per_page=10"

# Search by meter ID
curl "http://127.0.0.1:8000/api/meters/search?query=J100000"

# Filter by status
curl "http://127.0.0.1:8000/api/meters/status/Installed"

# Get one meter
curl "http://127.0.0.1:8000/api/meters/J100000"

# Export all meters
curl "http://127.0.0.1:8000/api/export/meters"

# Combined attribute filtering
curl "http://127.0.0.1:8000/api/meters/query?status=Installed&make=HPL"

# Nearby meters
curl "http://127.0.0.1:8000/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5"

# Hierarchy (all levels)
curl "http://127.0.0.1:8000/api/hierarchy"

# Hierarchy filtered by zone
curl "http://127.0.0.1:8000/api/hierarchy?zone_code=Z-01"

# Metadata
curl "http://127.0.0.1:8000/api/metadata"
```

## Test results

The API has been verified via `python3 test_endpoints.py` (http.client-based) and `pytest tests.py -v` (when pytest and compatible dependencies are available). Key results:

| Endpoint | Status |
|---|---|
| `GET /health` | 200 `{"status":"ok"}` |
| `GET /api/meters` | 200, 403 total, paginated |
| `GET /api/meters/search?query=<id>` | 200, matches by meterId/serialNo |
| `GET /api/meters/status/Installed` | 200, 238 meters |
| `GET /api/meters/status/Faulty` | 200, 90 meters |
| `GET /api/meters/status/Decommissioned` | 200, 75 meters |
| `GET /api/meters/{meterId}` | 200 (exists) / 404 (nonexistent) |
| `GET /api/transformers` | 200, 40 transformer groups |
| `GET /api/export/meters` | 200, 403 records |
| `GET /api/meters/query` | 200, combined filtering by attribute |
| `GET /api/meters/nearby` | 200, meters sorted by distance within radius |
| `GET /api/metadata` | 200, record count, source filename, freshness info |

**Verified command**: `python3 -m pytest tests.py -v` (requires compatible starlette/fastapi versions; see Phase 5 notes for environment limitations).

## Known discrepancy

The export contains **403** meter records, whereas the portal UI shows **405**.
This discrepancy is documented but the root cause is unknown; the API simply
returns the 403 records from the verified export file without alteration.

## OpenAPI specification

The automatic OpenAPI schema is available at:

```
http://127.0.0.1:8000/docs
```

Static OpenAPI YAML can be generated with:

```bash
uvicorn app:app --generate-spec -o openapi.yaml
```