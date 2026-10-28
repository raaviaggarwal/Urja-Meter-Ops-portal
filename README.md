# Flock Energy Meter API

A read-only FastAPI service that provides JSON access to a locally supplied
`meter-export.json` dataset. The export is intentionally not tracked because
permission to redistribute it is unverified. The service does **not** connect
to the live Urja Meter Ops portal or refresh data from it. Portal behavior and
what remains unverified are documented separately in
[docs/PROTOCOL.md](docs/PROTOCOL.md).

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
| `requirements.txt` | Pinned runtime and test dependencies verified with Python 3.12.4. |
| `openapi.json` | Checked-in OpenAPI 3.1 description for the API routes. |
| `docs/PROTOCOL.md` | Evidence-qualified observations of the live portal and local export. |
| `docs/API_DESIGN.md` | Earlier design notes; treat portal claims there as historical unless confirmed by `docs/PROTOCOL.md`. |

Other root-level scripts and reports are investigation or test artifacts, not
required runtime components.

## Requirements and installation

Use Python 3.12.4 (the version used for clean-environment verification).
From the repository root, install the pinned runtime and test dependencies:

```bash
python -m pip install -r requirements.txt
```

The application expects `meter-export.json` beside `app.py`. The real export
is not included in this repository. No environment variables or portal
credentials are required. The dataset is loaded into memory when the
application module is imported.

Use an authorized export if real data is required. To run the app and tests
without that export, copy the clearly synthetic fixture to the expected local
filename:

```powershell
Copy-Item tests/fixtures/meter-export.synthetic.json meter-export.json
```

The fixture uses synthetic identifiers, values, and hierarchy labels; it is
not portal data. `meter-export.json` remains ignored by Git. Without either
file, the app has no meter data and the data-dependent tests cannot pass.

## Validate and import a local JSON file

The ingestion CLI validates a local JSON array and writes it only to an
explicit `--output` path. For example, validate the synthetic fixture and
write a separate output file:

```bash
python ingest_meters.py tests/fixtures/meter-export.synthetic.json --output validated-meter-export.json
```

The CLI checks that each record is an object with a non-empty `meterId`,
string-valued required meter fields, all seven hierarchy levels with string
`name` and `code` fields, and finite latitude/longitude numbers in geographic
ranges. Additional fields are preserved and reported as warnings. Diagnostics
identify records by one-based index and field, but never print record values
or precise coordinates.

Malformed records and duplicate meter IDs make the entire input batch fail
with a nonzero exit code; no records are silently discarded and no output is
written. The first occurrence of an ID is used only as a reference when
reporting later duplicates. A valid batch is serialized to a temporary file
in the destination directory and atomically replaces the requested
destination. If validation or writing fails, an existing destination remains
unchanged. The input and output paths must be different.

This command imports and validates a file already available locally. It does
not retrieve data from the live portal, call a portal endpoint, or perform
authentication. The portal observations and unknowns remain documented in
[docs/PROTOCOL.md](docs/PROTOCOL.md).

## Start the API

Run this from the repository root:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

The service is available at `http://127.0.0.1:8000`. Interactive API
documentation is at `http://127.0.0.1:8000/docs`. The liveness route is
`GET /health`; it is intentionally excluded from the generated OpenAPI schema.

## API routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe; returns `{"status":"ok"}`. |
| `GET` | `/api/meters` | List records with pagination and optional search/status filters. |
| `GET` | `/api/meters/{meter_id}` | Get a meter record by ID. |
| `GET` | `/api/meters/search` | Search by meter ID or serial number substring. |
| `GET` | `/api/meters/status/{status}` | Filter by `Installed`, `Faulty`, or `Decommissioned`. |
| `GET` | `/api/meters/query` | Combine supported record attribute filters. |
| `GET` | `/api/meters/nearby` | Find records within a radius using their exported coordinates. |
| `GET` | `/api/hierarchy` | Return the hierarchy reconstructed from the export; supports `zone_code`. |
| `GET` | `/api/transformers` | Return unique DT groups derived from meter hierarchy records. |
| `GET` | `/api/export/meters` | Return all local export records. |
| `GET` | `/api/metadata` | Report local source-file metadata and static freshness policy. |

The checked-in [OpenAPI specification](openapi.json) documents the 10 API
operations under `/api`. `/health` is available at runtime but excluded from
that schema.

## Example request

With the server running, request installed meters made by HPL:

```bash
curl.exe "http://127.0.0.1:8000/api/meters/query?status=Installed&make=HPL"
```

For an authorized export, retrieve one record with:

```bash
curl.exe "http://127.0.0.1:8000/api/meters/J100000"
```

With the synthetic fixture, use `SYNTH-000001` in place of `J100000`.

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

Run the API and ingestion test suites with:

```bash
python -m pytest -q tests.py tests/test_ingestion.py
```

In an isolated Python 3.12.4 environment installed from `requirements.txt`,
the API and ingestion suites completed with **36 passed** and 7 deprecation
warnings (FastAPI `regex` parameters and Starlette's `httpx` TestClient
integration) using the synthetic fixture. No compatibility shim or global
package change was used. A separate Uvicorn HTTP regression run on port 8003
verified health, listing and pagination, search, meter detail, status
filters, transformer listing, export, hierarchy including
`zone_code=Z-01`, nearby search, metadata, validation/error responses, and
`/openapi.json`. The live OpenAPI route descriptions and methods matched the
checked-in [openapi.json](openapi.json) after regeneration with the pinned
environment. A fresh checkout can run the full suite by copying the synthetic
fixture as described above; an authorized export is only needed to exercise
the application against the real export.

## Future improvements

- Verify login and session behavior through a user-performed authorized
  browser session, then decide whether a live client is appropriate.
- Add integration tests for any future live client without recording session
  secrets.
- Revisit the FastAPI validation syntax and TestClient integration to resolve
  the deprecation warnings before upgrading the pinned dependency set.
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
