# Urja Meter Ops API — Current Implementation Report

This report replaces the earlier blocker snapshot. The API has been
implemented and regression-tested; the live portal client has not.

## Implementation

The repository contains a read-only FastAPI service that loads
`meter-export.json` at import time and serves its records from memory. The
real export is intentionally excluded from Git because redistribution
permission is unverified. A separately named synthetic fixture is available
for tests and demos; it contains no portal records. The service does not log
in to, refresh from, or otherwise connect to the live portal. The portal
evidence and unresolved protocol questions are maintained in
[docs/PROTOCOL.md](docs/PROTOCOL.md).

## Available routes

The application exposes the following routes:

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe; intentionally omitted from the OpenAPI schema. |
| GET | `/api/meters` | Paginated listing with optional search and filters. |
| GET | `/api/meters/search` | Search by meter ID or serial number substring. |
| GET | `/api/meters/{meter_id}` | Retrieve a meter by ID. |
| GET | `/api/meters/status/{status}` | Filter by installation status. |
| GET | `/api/meters/query` | Combine supported meter attribute filters. |
| GET | `/api/meters/nearby` | Find nearby records using exported coordinates. |
| GET | `/api/hierarchy` | Return the hierarchy derived from meter records, optionally filtered by zone. |
| GET | `/api/transformers` | Return unique DT groups derived from the export. |
| GET | `/api/export/meters` | Return the complete local export. |
| GET | `/api/metadata` | Return local dataset and file freshness metadata. |

The checked-in [openapi.json](openapi.json) is valid OpenAPI 3.1 JSON and
contains 10 documented `/api` operations with unique operation IDs.

## Recorded verification

- The isolated Uvicorn HTTP regression matrix returned successful responses
  for health, listing, search, status, meter detail, transformer groups,
  export, hierarchy, metadata, nearby, and query routes.
- Installed meter query returned HTTP 200 with total **238**. A combined
  filter returned **34** records.
- `GET /api/hierarchy?zone_code=Z-01` returned HTTP 200 with branches for
  `Z-01` only.
- Validation and missing-resource responses were checked; the missing-meter
  response returned 404 with structured error fields.
- The current clean-environment HTTP run also confirmed the README sample
  (`status=Installed&make=HPL`) returned HTTP 200, total 46, with 20 returned
  records matching both filters.
- The served OpenAPI JSON matches the checked-in file exactly; it contains 10
  unique documented API operation IDs. The `/health` endpoint is intentionally
  excluded from the schema.
- A fresh Python 3.12.4 virtual environment installed from
  `requirements.txt` passed `python -m pytest -q tests.py`: **17 passed, 7
  deprecation warnings**, without a compatibility shim or global package
  changes. `pip check` reported no broken requirements.
- The same 17-test suite passed against the synthetic fixture in an isolated
  copy; installed-meter query returned 238 and zone filtering returned only
  `Z-01`.
- An earlier unpinned global environment had a Starlette/httpx TestClient
  incompatibility. The pinned clean environment resolved that setup problem.
- A Uvicorn HTTP regression run on port 8003 passed the documented sample and
  route assertions. The served `/openapi.json` now matches the checked-in
  file exactly; it has 10 unique API operation IDs. The checked-in schema was
  regenerated after investigating the previous differences, which were
  generated-schema changes between the old and current FastAPI/Pydantic
  versions.

## Data and portal evidence

The local export contains **403 records**. The authenticated portal listing
was later observed to show **403 total**. Older investigation documents
reported 405, but the cause of that discrepancy is unknown and the earlier
count is not treated as verified. See [docs/PROTOCOL.md](docs/PROTOCOL.md)
for the scoped browser captures and export measurements.

Portal meter-list search, pagination, and `J100000` geography/energy requests
were observed in the authorized browser. The login submission, authentication
mechanism, session expiry, transformer data requests, and several other
portal behaviors remain unverified. These observations do not make this
service a live portal client.

## Limitations and next work

- Data is a static local export; it is not refreshed and can become stale.
- A fresh checkout must provide an authorized export or manually copy the
  synthetic fixture to `meter-export.json` before running the app or tests.
- No live authentication, portal session management, or portal data client is
  implemented.
- Consumption observations and richer portal detail data are not integrated
  into the local API.
- The verified Python 3.12.4 dependency set is pinned in `requirements.txt`;
  deprecation warnings should be addressed before changing that set.
- If live integration is approved, verify the remaining portal protocol
  behavior first, then add a client and tests without recording secrets.

## Documentation

- [README.md](README.md) contains installation, startup, API examples, design
  notes, intentional omissions, future improvements, and the five assignment
  reflection answers.
- [docs/PROTOCOL.md](docs/PROTOCOL.md) is the evidence-qualified record of
  portal and local-export findings.
- [openapi.json](openapi.json) describes the API operations.
