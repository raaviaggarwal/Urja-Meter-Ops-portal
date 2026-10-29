# Flock Energy Meter API

A read-only FastAPI service that provides JSON access to a locally supplied
`meter-export.json` dataset. The export is intentionally not tracked because
permission to redistribute it is unverified. The service does **not** connect
to the live Urja Meter Ops portal or refresh data from it. See the
[API's OpenAPI specification](openapi.json) and the evidence-qualified
[portal protocol notes](docs/PROTOCOL.md) for details.

## Project structure

| Path | Purpose |
|---|---|
| `app.py` | FastAPI application, in-memory dataset loading, indexes, and routes. |
| `meter_ingestion.py` | JSON record validation and atomic output helpers. |
| `ingest_meters.py` | CLI for validating and importing a local JSON file. |
| `meter-export.json` | Locally supplied source dataset; excluded from Git pending redistribution approval. |
| `tests/fixtures/meter-export.synthetic.json` | Synthetic-only fixture for test and demo use; contains no portal records. |
| `tests.py` | API behavior tests. |
| `tests/test_ingestion.py` | Synthetic-only ingestion pipeline tests. |
| `tests/test_dataset_loading.py` | Synthetic-only dataset validation and snapshot metadata tests. |
| `tests/test_api_filtering.py` | Regression tests for combined filter AND semantics. |
| `tests/test_openapi_contract.py` | Checks that the checked-in OpenAPI contract matches the application. |
| `requirements.txt` | Pinned runtime and test dependencies verified with Python 3.12.4. |
| `openapi.json` | Checked-in OpenAPI 3.1 description for the API routes. |
| [`gen_openapi.py`](gen_openapi.py) | Regenerates `openapi.json` from the FastAPI application. |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | Evidence-qualified observations of the live portal and local export. |
| [docs/API_DESIGN.md](docs/API_DESIGN.md) | Earlier design notes; treat portal claims there as historical unless confirmed by `docs/PROTOCOL.md`. |
| [PORTAL_INVESTIGATION.md](PORTAL_INVESTIGATION.md) | Current evidence summary and comparison of observed portal capabilities with the local API. |

Other root-level scripts and reports are investigation or test artifacts, not
required runtime components.

## Requirements and installation

Use Python 3.12.4 (the version used for clean-environment verification).
From the repository root, create and activate a virtual environment, install
the pinned runtime and test dependencies, and use only synthetic data for a
clean checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (Test-Path .\meter-export.json) {
    throw "meter-export.json already exists; inspect it before replacing it."
}
Copy-Item .\tests\fixtures\meter-export.synthetic.json .\meter-export.json
```

The fixture contains fabricated identifiers, values, coordinates, and
hierarchy labels for local demonstration and tests only; it is not portal
data and must not be used as evidence about real meters. The real export is
not committed because redistribution permission is unverified. If using a
local authorized export instead, place it beside `app.py` without overwriting
an existing file. `meter-export.json` is ignored by Git.

The application requires a `meter-export.json` file beside `app.py`. On
import, it validates the dataset using the ingestion validator. A missing,
unreadable, malformed, or invalid dataset causes application startup to fail
with a record/field diagnostic; it is never silently replaced with an empty
dataset. No environment variables or portal credentials are required.

The API loads one validated dataset snapshot when the application module is
imported. `/api/metadata` reports the source file's modification time captured
for that loaded snapshot. Editing or replacing the file while the process is
running does not refresh the in-memory data or its reported timestamp; restart
the application to load a new snapshot. This is local-file freshness only and
does not indicate live portal updates.

## Validate and import a local JSON file

The ingestion CLI validates a local JSON array and writes it only to an
explicit `--output` path. For example, validate the synthetic fixture and
write a separate output file:

```powershell
python ingest_meters.py .\tests\fixtures\meter-export.synthetic.json --output validated-meter-export.json
```

The CLI checks that each record is an object with a non-empty `meterId`,
string-valued required meter fields, all seven hierarchy levels with string
`name` and `code` fields, and finite latitude/longitude numbers in geographic
ranges. Additional fields are preserved and reported as warnings. Diagnostics
identify records by one-based index and field, but never print record values
or precise coordinates.

Malformed records and duplicate meter IDs make the entire input batch fail
with a nonzero exit code; no records are silently discarded and no output is
written. The `duplicate_ids` summary counts occurrences after the first;
that first occurrence is used only as a reference when reporting later
duplicates. A valid batch is serialized to a temporary file
in the destination directory and atomically replaces the requested
destination. If validation or writing fails, an existing destination remains
unchanged. The input and output paths must be different.

This command imports and validates a file already available locally. It does
not retrieve data from the live portal, call a portal endpoint, or perform
authentication. The portal observations and unknowns remain documented in
[docs/PROTOCOL.md](docs/PROTOCOL.md).

## Start the API

Activate the virtual environment in the server terminal, then run this from
the repository root:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

The service is available at `http://127.0.0.1:8000`. Interactive API
documentation is at `http://127.0.0.1:8000/docs`. The liveness route is
`GET /health`; it is intentionally excluded from the generated OpenAPI schema.
In a separate PowerShell window, activate the same virtual environment and
run the tests from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

## API routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe; returns `{"status":"ok"}`. |
| `GET` | `/api/meters` | List records with pagination, search, status, phase, build, zone, division, and DT filters; supplied filters combine with AND semantics. |
| `GET` | `/api/meters/{meter_id}` | Get a meter record by ID. |
| `GET` | `/api/meters/search` | Search by meter ID or serial number substring. |
| `GET` | `/api/meters/status/{status}` | Filter by `Installed`, `Faulty`, or `Decommissioned`. |
| `GET` | `/api/meters/query` | Combine status, make, phase, install type, DT, zone, circle, and feeder filters with AND semantics. |
| `GET` | `/api/meters/nearby` | Find records within a radius using their exported coordinates. |
| `GET` | `/api/hierarchy` | Return the hierarchy reconstructed from the export; supports `zone_code`. |
| `GET` | `/api/transformers` | Return unique DT groups derived from meter hierarchy records. |
| `GET` | `/api/export/meters` | Return all local export records. |
| `GET` | `/api/metadata` | Report local source-file metadata and static freshness policy. |

The checked-in [OpenAPI specification](openapi.json) documents the 10 API
operations under `/api`. `/health` is available at runtime but excluded from
that schema. Query validation failures return 422; invalid nearby coordinates
return 400; unknown meter IDs and zone codes return 404; unexpected server
errors return a generic 500 response. The nearby latitude/longitude ranges
are shown in the schema, while out-of-range values preserve the API's explicit
400 behavior. Typed response schemas describe the stable fields returned by
each route. Meter-detail and export models preserve additional fields present
in the validated local export rather than discarding them.

After changing route definitions, regenerate the checked-in specification
with `python gen_openapi.py` from the repository root while a valid local
dataset is available.

## Example request

With the synthetic fixture and server running, search the local snapshot:

```bash
curl.exe "http://127.0.0.1:8000/api/meters?search=SYNTH-000001"
```

Representative response (all values are synthetic):

```json
{
  "meters": [
    {
      "meterId": "SYNTH-000001",
      "serialNo": "SYNTH-SERIAL-000001",
      "make": "SyntheticCo",
      "phaseType": "single",
      "installStatus": "Installed",
      "dtCode": "DT-SYNTH-001",
      "hierarchy": {
        "zone": {"name": "Synthetic zone 01", "code": "Z-01"},
        "dt": {"name": "Synthetic transformer 001", "code": "DT-SYNTH-001"}
      },
      "geo": {"lat": 0.0, "lng": 0.0}
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

This is the summary shape returned by `/api/meters`; meter-detail and export
routes return the complete local record instead.

## Assumptions and design trade-offs

- **Local export as the data source:** Portal login mechanics and session
  behavior have not been verified. This implementation therefore serves the
  local `meter-export.json` file and does not imply live portal access. The
  real export is excluded from Git pending redistribution authorization; a
  synthetic fixture is provided for safe local testing and demonstration.
  Before running the app or tests from a fresh checkout, copy
  `tests/fixtures/meter-export.synthetic.json` to `meter-export.json`, or
  supply an authorized real export at that path.
- **Read-only, in-memory processing:** The dataset is small and loaded once at
  import. This avoids repeated disk reads and keeps the service simple, but
  changes to the export require restarting the process; this approach may not
  suit a much larger or frequently updated dataset.
- **Use only available fields:** Hierarchy and transformer-group responses
  are derived from fields present in the export. The API does not invent
  transformer ratings or other missing attributes.
- **Nearby search uses exported coordinates:** Distance is calculated using
  the Haversine formula. Results cannot be more accurate than the source
  coordinates.
- **Freshness is local-file freshness:** Metadata reports the file's local
  modification time, not the time of the latest portal update.

## Intentionally not implemented

- **Live portal client, login/session management, and automatic refresh:** The
  login request/response, authentication mechanism, and session expiry remain
  unverified. A client would require further authorized observation.
- **Consumption proxy and portal transformer-detail proxy:** The export does
  not contain consumption time series or full transformer specifications.
  Some meter-detail data was observed in the portal, but it is not integrated
  into this local-data service.
- **Write operations or a portal UI:** The service is read-only and the task
  here is an API over the export, not a portal replacement.

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for what was actually observed in the
portal and what remains unknown.

## Tests and verification

The complete suite covers API behavior, ingestion, dataset loading, combined
filters, and OpenAPI consistency:

```bash
python -m pytest -q
```

On 2026-10-28, the complete suite passed with **41 passed and no warnings** in
an isolated Python 3.12.4 environment installed from `requirements.txt`; the
suite used only the synthetic fixture. The pinned Starlette TestClient uses
the supported `httpx2` package. The OpenAPI consistency test compares the
checked-in file with the application-generated schema.

## Future improvements

- Verify login and session behavior through a user-performed authorized
  browser session, then decide whether a live client is appropriate.
- Add integration tests for any future live client without recording session
  secrets.
- Add explicit dataset provenance/version metadata and a documented refresh
  process.
- Expand response-model and edge-case tests, especially for filters and
  hierarchy data with missing codes.
- Consider persistent storage or indexing if the dataset grows substantially.

## Reflection

### What assumptions did you make?

I treated `meter-export.json` as the API's available source of record and
kept the service read-only. I did not assume the live portal login mechanism
or session behavior because those were not captured. Derived transformer and
hierarchy data is limited to relationships represented in the export.

### Which part was the most difficult, and how did you get unstuck?

The hardest part was separating portal behavior from what could be proven in
the local export and earlier investigation notes. Capturing actual browser
requests and checking the local API over HTTP helped distinguish observations
from assumptions and identify routing and hierarchy defects.

### If you had another day, what would you improve?

I would first verify the authorized login/session flow and additional portal
data surfaces, then decide whether to build a live client. I would also make
the Python dependency and test environment reproducible and add broader
automated coverage for filters and hierarchy edge cases.

### What mistake did you make while solving this?

Earlier notes treated some authentication details and a 405 portal count as
verified despite conflicting evidence. I corrected the protocol record to
classify those points as unverified or historical and retained only supported
observations.

### If you were reviewing your own submission, what would you criticise?

The service is backed by a static export rather than a verified live client,
so its data can become stale. FastAPI, Starlette, and httpx are pinned in
`requirements.txt`, though the current set emits deprecation warnings. The
portal protocol still has unresolved authentication, filtering, and
session-expiry questions.
