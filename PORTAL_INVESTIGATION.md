# Portal Data Retrieval Investigation

**Investigation date:** 2026-10-28
**Scope:** Read-only comparison of authorized browser observations, retained
sanitized network evidence, the local export schema, and this repository's
API. No credentials, cookies, tokens, precise coordinates, or meter/customer
values are reproduced here.

## Executive summary

The retained authenticated-browser captures document a paginated meter-search
request and separate geography and energy requests for one meter. They show
that consumption data is available from the portal, but not in the local
export. The portal detail page displayed a hierarchy path and a consumption
table. No captured request for transformer/hierarchy data or export behavior
is available.

The shared browser showed a meter detail page in an earlier authorized
session. In the earlier Phase 2 navigation, `GET /meters` was followed by
`GET /login`; the login document returned 200, but the initial response status
and redirect cause were not captured. During Phase 13, the currently shared
page again displayed `/login`. No login was attempted, and no fresh
authenticated request/response capture was made.
Network findings below are explicitly attributed to retained evidence in
[`docs/PROTOCOL.md`](./docs/PROTOCOL.md), not represented as newly captured
requests.

The latest retained portal listing observation and the local export aggregate
check both report 403. Historical notes that report 405 conflict with these
observations; their cause is unknown.

## Evidence and confidence

Confidence describes the stated, limited finding—not generalizes beyond it.

| Finding | Evidence source and scope | Confidence | Remaining uncertainty |
|---|---|---:|---|
| Phase 13 shared browser currently displays `/login` | Direct browser page snapshot; no response status or redirect chain captured in this phase | High | Why it is at the login page and whether a previous session expired |
| Meter detail UI displays a meter summary, location, a hierarchy path, and a consumption table | Shared-browser page snapshot before the reload; one detail page | High | Whether all meters have the same fields or content |
| The UI hierarchy path displays zone, circle, division, subdivision, substation, feeder, and DT | Same detail-page snapshot; one meter | High | Whether these relationships are available from a separate portal hierarchy endpoint |
| Meter search/listing is requested by `GET /portal/meters/search` with `q` and `page` query parameters | Retained Phase 2.1 captures described in `docs/PROTOCOL.md`; pages 1, 2, 4 and one search | High for observed requests | Other filters, search by serial, pagination response fields, and error behavior |
| Search endpoint returns JSON with a top-level `data` array and meter summary fields | Retained response summaries for pages 1, 2, and 4 | High for observed shape | Full response schema and page metadata |
| Geography and energy are separate JSON requests | Retained Phase 2.1 responses for one meter | High for that meter | Whether all meters have data or the same schema |
| Login form declares POST `/login` and URL-encoded fields named `email` and `password` | Retained observation of form attributes; no submission captured | High for form markup | Actual login request/response, authentication mechanism, redirects, and session expiry |
| Successful authentication uses a specific cookie or token | No direct evidence | Unknown | Do not assume cookie/session implementation |
| Portal rate limits or status filters | Not exercised or captured | Unknown | Behavior and limits |

No request headers, request bodies, authentication material, or sensitive
response values were inspected or included in this report.

## Sanitized portal request evidence

The requests below are retained captures summarized in
[`docs/PROTOCOL.md`](./docs/PROTOCOL.md). They were not recaptured during this
investigation because the shared browser navigated to the sign-in page.
Dynamic meter identifiers and search terms are masked.

| Observed request | Observed response | Confirmed shape |
|---|---|---|
| `GET /portal/meters/search?q=&page=1` | 200, `application/json` | Top-level `data` array; visible record fields: `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, `dtCode` |
| `GET /portal/meters/search?q=&page=2` | 200, `application/json` | Top-level `data` array with different page records |
| `GET /portal/meters/search?q=&page=4` | 200, `application/json` | 20 records observed |
| `GET /portal/meters/search?q=<redacted>&page=1` | 200 | UI showed one matching record; response body schema not verified |
| `GET /meters/{meterId}/__data.json` | 200, `application/json` | SvelteKit page-data object with top-level `type` and `nodes` keys |
| `GET /portal/meters/{meterId}/geo` | 200, `application/json` | Object with `data.latitude` and `data.longitude`; values omitted |
| `GET /portal/meters/{meterId}/energy` | 200, `application/json` | Top-level `data` array; visible fields include `timestamp`, `kwh`, `kvah`, and `voltR`; values omitted |

The detail-page snapshot showed a consumption table with timestamp, kWh, kVAh,
and V(R) columns. The captured energy response is from one meter only. Units
beyond the displayed field labels, timestamp timezone, interval completeness,
date-range parameters, and pagination are unverified.

The listing UI was previously observed to show 403 total, 20 rows per page,
and 21 pages. Page navigation issued the observed `page` requests. The JSON
pagination fields were not inspected, so the UI display must not be treated
as evidence of a particular response metadata schema. Rate limits were not
tested.

## Local export and API comparison

The real local export was read only for aggregate/schema facts; no record
values were emitted. It contains **403 records**, **403 unique non-null IDs**,
no missing or duplicate IDs, and geographic objects on all records. Its
top-level fields are `meterId`, `serialNo`, `make`, `phaseType`,
`installStatus`, `installType`, `build`, `dtCode`, `hierarchy`, and `geo`.
The nested hierarchy contains `zone`, `circle`, `division`, `subdivision`,
`substation`, `feeder`, and `dt`. A recursive field-name scan found no
consumption, energy, reading, kWh, or kVAh fields.

The source file remains unchanged. Its presence in the local workspace does
not establish permission to redistribute it.

| Portal capability or data | Current API coverage | Evidence | Recommended next step |
|---|---|---|---|
| Meter list, query, and pagination | Local-export listing at `GET /api/meters`; filters and paging are implemented. It is not a portal proxy. | Current `app.py` and synthetic/API tests; portal list/search evidence above | Keep sources clearly separated; verify portal filter semantics before attempting parity |
| Meter search | `GET /api/meters/search` searches local meter ID or serial; `/api/meters` also combines search with its supported filters | Portal capture establishes query parameter `q` for an observed meter-ID search only | Verify serial search and edge cases in an authorized browser session |
| Individual meter detail | `GET /api/meters/{meter_id}` returns the complete local export record | Current route and local schema; portal detail page directly observed | Compare additional authorized detail fields before claiming parity |
| Consumption/energy | No current API route and no consumption data in the local export | Portal energy request captured for one meter; local schema scan | Do not implement a portal fetcher until auth/session behavior and a safe data-handling design are approved; first verify schema and coverage for more than one meter |
| Geography | `GET /api/meters/nearby` uses local export coordinates; meter detail route exposes the local `geo` object | Portal geo request captured for one meter; export contains geographic objects | Confirm field coverage and handling in more authorized detail records |
| Hierarchy | `GET /api/hierarchy` reconstructs a tree from local records; `GET /api/transformers` derives DT summaries | Portal detail UI shows a hierarchy path; local export contains hierarchy levels | Inspect the portal Transformers page/network requests before asserting parity or relationship semantics |
| Portal export/bulk download | No verified portal export request; no live integration in this API | No captured export request; README and API code identify local-file operation | Observe an explicit export action in the browser, if available and authorized |
| Authentication/session handling | Not implemented by this local API | Login form markup observed; login submission and expiry remain unverified | Do not add authentication automation based on form markup alone |

The route inventory and schemas are documented in
[`openapi.json`](./openapi.json). The local API's OpenAPI description does not
declare a portal data source.

## Meter-count comparison

- The local export currently has 403 records and 403 unique non-null IDs
  (aggregate check performed during this investigation).
- The latest retained authenticated listing observation showed 403 total.
- Therefore, there is **no count discrepancy in those observations**.
- Earlier investigation notes reported 405. Those reports conflict with the
  later 403 observation; the reason for the older count is not established.
- A matching count does not prove that the portal and export contain identical
  records or fields. Prior local comparisons covered five listing rows and
  six visible fields only; see `docs/PROTOCOL.md`.

## Recommended next implementation phase

Do not implement live portal retrieval or a consumption endpoint yet. The
smallest contract-focused improvement supported by local evidence—typed
Pydantic response models for existing API routes—has now been implemented and
checked against synthetic API responses and the generated OpenAPI document.
This improves the API contract without claiming portal parity.

A consumption endpoint is not yet sufficiently specified. Before designing
one, use a user-authorized browser session to confirm energy response
structure, coverage across several meters, time range, and timestamp
semantics. Then seek approval for a synthetic-only fixture and input
contract; do not copy portal readings into the repository.

## Open questions and blockers

- What is the actual successful login request/response and authentication
  mechanism? This was not captured; no login was attempted here.
- What are the energy response's full data coverage, interval, timezone, units,
  date filtering, and error behavior?
- What request and response provide transformer data, and what relationships
  does the portal explicitly expose?
- Does the search endpoint support serial number, status filters, or other
  parameters?
- What are the exact JSON pagination fields, and are there rate limits?
- What explains older reports of 405 when the later portal UI and local export
  both show 403?

## Phase 12 files and verification

Phase 12 added this report only; no application, test, OpenAPI, or dataset
files were changed in that phase. No live login or unauthorized request was
attempted. All figures in this report are aggregate or schema-level;
meter/customer values and authentication material are omitted.
