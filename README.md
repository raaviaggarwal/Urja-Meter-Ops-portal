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
| `GET` | `/api/transformers` | Hierarchy‑derived transformer summary. |
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
```

## Known discrepancy

The export contains **403** meter records, whereas the portal UI shows **405**.
This discrepancy is documented but the root cause is unknown; the API simply
returns the 403 records from the verified export file without alteration.

## Tests

```bash
pytest tests.py -v
```

## OpenAPI specification

The automatic OpenAPI schema is available at:

```
http://127.0.0.1:8000/docs
```

Static OpenAPI YAML can be generated with:

```bash
uvicorn app:app --generate-spec -o openapi.yaml
```