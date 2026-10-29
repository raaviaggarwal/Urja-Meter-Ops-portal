# Urja Meter Ops — Portal and Export Evidence

This document records retained observations from earlier browser sessions,
local-export measurements, and the Phase 13 browser state. The earlier
authenticated captures were not repeated during Phase 13. It does not describe
an API integration. No credentials, cookies, or tokens are recorded here.
The local-export measurements below are retained results from the earlier
investigation; the real export is absent from the current worktree and was not
re-read during the final submission audit.

## Evidence classifications

- **Verified by direct observation** — seen in the shared browser at the
  stated date and phase. UI observations do not establish the underlying HTTP
  response format or request implementation.
- **Verified by captured request/response or existing test** — supported by a
  retained request/response or a reproducible local test.
- **Inferred but not confirmed** — plausible from the notes or UI, but not
  established by direct evidence in the retained evidence set.
- **Unknown** — not established by available evidence. Earlier authenticated
  portal observations exist, but the current Phase 13 browser is at `/login`
  and no fresh authenticated request/response capture was made.

## 1. Live portal observations

### Availability observations

- **2026-10-27 18:34:42.633 UTC:** The integrated browser was at
  `https://urja-ops.flockenergy.tech/meters`. Its page snapshot showed HTTP
  502/error content, and the browser console recorded a failed resource with
  status 502. This is evidence of a 502 for that page observation, not that
  the entire portal was down.
- **2026-10-28:** The base URL was subsequently opened in the same shared
  browser session. It navigated to `/meters`, where the signed-in Meters page
  rendered. The exact time of this later observation was not captured.
- **2026-10-28 (Phase 2 investigation):** The shared browser was initially
  attached to a meter detail page, but navigating to `/meters` ended at the
  sign-in page. The observed navigation chain was `GET /meters` followed by
  `GET /login`; the final `/login` document returned HTTP 200. The status of
  the initial `/meters` response was not captured. This establishes the
  access state during that investigation only; it does not establish why the earlier
  signed-in state was no longer present.
- **2026-10-28 (Phase 13 check):** The currently shared browser page displays
  the sign-in form at `/login`. No login was attempted and no fresh
  authenticated network capture was made. This does not establish session
  expiry or the cause of the earlier redirect.
- **Phase 2.1:** After the user manually signed in through the normal browser
  flow, the shared browser displayed the Meters page and an individual meter
  detail page. The sign-in submission itself was not observed. Network
  captures below are from this authenticated browser session; no credentials
  or authentication headers were inspected. The exact capture time was not
  recorded.

### Meter listing visible in the browser

**Verified by direct observation on 2026-10-28:**

- The page was titled **Meters** and displayed **403 total**.
- The table showed 20 records on **Page 1 of 21**. Visible columns were
  `METER`, `SERIAL`, `MAKE`, `PHASE`, `STATUS`, and `DT`.
- Five displayed records were compared with `meter-export.json`. For all five,
  `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, and `dtCode`
  matched the local export exactly.
- This comparison verifies those displayed fields for those five records
  only. It does not validate other fields or prove that the local export and
  portal remain globally identical.

The latest retained UI observation recorded **403**, matching the local
export measurement. Earlier notes reporting 405 portal meters conflict with
that observation; the cause of the historical count is not established.

The page visibly exposes navigation to Meters, Transformers, Ops Desk, and
Sign out. The Transformers page contents were not examined in Phase 2.1.

**Verified by direct observation during Phase 2.1:** The listing search box
accepted a meter-ID query and displayed one matching row. Clicking Next changed the
displayed page while the browser remained at `/meters`.

## 2. Authentication and session behavior

**Verified by direct observation in earlier browser sessions:** The sign-in
page at `/login` displayed Email and Password inputs. The form's declared
method is POST, action is `/login`, and encoding is
`application/x-www-form-urlencoded`; its input names are `email` and
`password`. These are form attributes, not a captured submission. In an
earlier signed-in listing observation, the page displayed a Sign out control.

**Reported by earlier investigation notes, not supported by a retained
request/response:** Those notes describe a failed-login JSON response and requests
involving browser headers. The notes conflict on whether successful login was
actually achieved and whether a session cookie was observed. No login
submission was captured in Phase 2.1; the user reported completing
sign-in manually. No login request/response was captured to resolve those
conflicts.

**Unknown:** The successful login request and response, exact authentication
mechanism, redirect behavior, whether any additional request headers are
required, and session expiry or revocation behavior. Authenticated page data
requests succeeded in the shared browser, but that does not establish which
authentication mechanism enabled them. Do not treat the framework-based
cookie explanation in earlier notes as confirmed.

## 3. Portal routes, data requests, and response formats

**Verified by captured request/response during Phase 2.1** (same origin
`https://urja-ops.flockenergy.tech`; response bodies were inspected only for
non-sensitive structure):

| Observed request | Response | Observed shape |
|---|---|---|
| `GET /portal/meters/search?q=&page=1` | 200 OK, `application/json`, Content-Length `2539` | JSON top-level `data` array; visible record fields include `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, and `dtCode`. |
| `GET /portal/meters/search?q=&page=2` | 200 OK, `application/json`, Content-Length `2518` | JSON top-level `data` array; visible record fields include `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, and `dtCode`. |
| `GET /portal/meters/search?q=&page=4` | 200, `application/json` | 20 records were returned; visible record fields include `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, and `dtCode`. Response pagination fields have not been verified. |
| `GET /portal/meters/search?q=<redacted>&page=1` | 200 OK; approximately `0.2 kB` transferred in the DevTools capture | The UI displayed one matching record and “Page 1 of 1”; identifier and summary values omitted. The response body schema was not verified from this capture. |
| `GET /meters/{meterId}/__data.json` | 200, `application/json` | SvelteKit page-data response; top-level keys observed: `type`, `nodes`. |
| `GET /portal/meters/{meterId}/geo` | 200 OK, `application/json`, Content-Length `74` bytes | Object with numeric `data.latitude` and `data.longitude` fields; values omitted. |
| `GET /portal/meters/{meterId}/energy` | 200 OK, `application/json`, Content-Length `27557` bytes | Top-level `data` array; entries expose `timestamp`, `kwh`, `kvah`, and `voltR`; sample values omitted. |

**Chrome DevTools capture:** In both page 1 and page 2 requests, `q` was empty
and `page` was the requested page number. After navigating to page 2, the UI
displayed “Page 2 of 21” and different meter rows. The response pagination
fields in these two DevTools captures have not yet been inspected; the
Content-Length values above do not establish record totals or page metadata.

Separately, a captured page 4 response contained 20 records. The DevTools
search capture shows that a meter-ID search issued
`q=<redacted>&page=1`; the UI then displayed the single matching record listed
above. These observations establish this specific query and page navigation
behavior for the session; they do not establish status filtering,
search-by-serial behavior, or a response pagination schema.

The geography and energy observations above are from one meter detail page
only; they do not establish that other meters behave identically. No units
or timestamp timezone are inferred from the energy values. The meter detail
page was rendered as an HTML document in the browser
(`document.contentType` was `text/html`); its document response content-type
header was not exposed by the capture tool. The detail UI showed meter
nameplate fields and a hierarchy path through zone, circle, division,
subdivision, substation, feeder, and DT. JSON data for geography and energy
was fetched separately as shown above. The listing's rendered content alone
does not prove it came from the JSON endpoint; the captured search response
does confirm the endpoint and format used during search and pagination.

The successful login request and response, exact authentication mechanism,
and session expiry or revocation behavior remain unknown. The literal route
strings `/(portal)/meters` and `/(portal)/transformers` in
older notes were not observed as request URLs in this capture; do not treat
them as such. No request bodies, request headers, or authentication material
were inspected.

## 4. Local export: verified findings

The following measurements are from the repository's `meter-export.json`, not
from an assumed live API:

- **403 raw records**
- **403 unique, non-null meter IDs**
- **No missing or blank IDs**
- **No duplicate IDs**
- IDs form a contiguous sequence with no gaps; endpoint values are omitted
- **No missing or invalid coordinates:** every record has numeric latitude
  and longitude within valid geographic ranges
- Status counts: Installed **238**, Faulty **90**, Decommissioned **75**
- Make counts: Allied **76**, Genus **88**, HPL **90**, L&T **64**, Secure
  **85**
- DT codes: DT-001 through DT-040; each has 10 records except DT-007, which
  has 13
- The explicit `dtCode` agrees with `hierarchy.dt.code` in every record

Each export record has these top-level fields: `meterId`, `serialNo`, `make`,
`phaseType`, `installStatus`, `installType`, `build`, `dtCode`, `hierarchy`,
and `geo`. The export hierarchy has `zone`, `circle`, `division`,
`subdivision`, `substation`, `feeder`, and `dt` objects. These findings
describe the local file; they do not establish that the portal exposes the
same full record schema.

No retained evidence establishes the export button's request path or whether
the local file was produced by the portal's current export behavior.

## 5. Pagination, filtering, and rate limits

- **Verified by direct observation and captured response:** The listing showed
  403 total and 20 rows per page, with Page 1 of 21. Clicking Next produced a
  `page=2` request with an empty `q`; the UI then showed Page 2 of 21 and
  different rows. The corresponding DevTools JSON pagination fields remain
  uninspected.
- **Verified by captured request and UI observation:** Searching for a meter ID
  used `GET /portal/meters/search?q=<redacted>&page=1`; the UI showed
  one matching record and “Page 1 of 1”. The response pagination fields have
  not been inspected.
- **Unknown:** Search by serial number, status/filter controls and parameters,
  any behavior beyond the observed pages and search, and rate limits. No
  rate-limit behavior was tested.

## 6. Evidence status by claim

| Claim | Classification | Evidence and limitation |
|---|---|---|
| Local export has 403 records and 403 unique IDs | Verified by direct observation | `meter-export.json`; counts and uniqueness were recalculated |
| IDs form a contiguous sequence with no gaps | Verified by direct observation | The full numeric interval was checked; endpoint values omitted |
| Export coordinates are present and valid | Verified by direct observation | All 403 records checked for numeric latitude/longitude ranges |
| Portal listing showed 403 records and 20 rows on page 1 of 21 | Verified by direct observation | Authenticated browser UI on 2026-10-28 |
| Five portal rows match export values for six visible fields | Verified by direct observation and local comparison | Five sample rows; no claim about unobserved fields |
| `/meters` showed 502 | Verified by direct observation | Browser event timestamp 2026-10-27 18:34:42.633 UTC |
| Base URL later led to a rendered meter listing | Verified by direct observation | Same shared browser session; 2026-10-28 |
| Phase 2 navigation to `/meters` ended at `/login`, final document 200 | Verified by browser navigation | Initial response status was not captured; the user later manually signed in for Phase 2.1 |
| Authenticated listing and meter detail pages were accessible after the user manually signed in | Verified by direct observation | Phase 2.1; login submission was not captured |
| Listing search and pagination use `/portal/meters/search` with JSON responses | Verified by captured request/response | Search `q=<redacted>&page=1`; page request `q=&page=4`; captures summarized in section 3 |
| Meter geography and energy data use the observed `/portal/meters/{meterId}/geo` and `/energy` requests | Verified by captured request/response | Both returned HTTP 200 `application/json`; one meter only |
| Login form declares POST `/login` with form encoding and `email`/`password` input names | Verified by direct observation of form attributes | No form submission or request body observed |
| Login is form-based and its failure response has a particular JSON shape | Inferred but not confirmed | Described in earlier notes; no request/response capture is available |
| A successful login sets a session cookie | Inferred but not confirmed | No login response or authentication material was inspected |
| Session expiration behavior | Unknown | Not observed or tested |
| Status filtering and search by serial number | Unknown | Not exercised in Phase 2.1 |
| Transformer data requests and response fields | Unknown | Transformers page not inspected |
| 405 portal records | Not supported by the latest retained observation | Earlier notes report 405; the retained listing observation reports 403 |

## 7. Earlier investigation notes and limitations

`docs/API_DESIGN.md`, `README.md`, `Final_Report.md`, and
`AUDIT_OUTPUT.md` contain historical claims. They are not independent
evidence by themselves. In particular:

- Some notes label authentication details as verified while also saying that
  valid credentials or successful authenticated access were unavailable.
- The notes disagree on the portal count (405 versus 403) and on the evidence
  for successful authentication.
- Proposed API endpoints in API design documents describe a proposed service,
  not confirmed portal endpoints.
- Local application test results verify the local API against the export; they
  do not prove live portal protocol behavior.
- Earlier investigation notes claim that authenticated portal responses
  were HTML-only and record `/(portal)/...` route strings as request paths.
  The Phase 2.1 capture instead observed JSON requests at the paths listed in
  section 3; treat the older request-format and path claims as unverified or
  superseded by this capture.

Claims should be promoted to verified status only when supported by a
reproducible capture or a directly observed portal result with its scope
recorded.

## 8. Checks still required

The Phase 13 shared browser currently displays `/login`; no fresh
authenticated captures were made. The following protocol details remain
unverified:

1. To verify the login flow, capture the request and response during a future
   user-performed normal sign-in, without recording credentials or session
   material; verify redirect and successful authentication behavior.
2. Observe the actual data-fetching requests for transformer data and export;
   record paths, methods, parameters, status codes, content types, and
   sanitized response shapes. Do not guess endpoints.
3. Exercise search by serial number and any status/filter controls if present,
   then compare the responses with what the UI displays.
4. Observe session expiry or revocation safely and record the actual resulting
   UI/request behavior.
5. The requested independent comparison of five meters is complete for the
   six fields visible in the listing. Compare additional record fields and
   investigate any future discrepancies between portal and export. Select
   meter IDs directly from the live listing across different pages and
   statuses, record the portal's displayed values first, then compare those
   observations with the corresponding export records. Use the live meter
   detail UI for fields not shown in the listing; do not treat the export or
   the local API as independent evidence of itself.
6. Inspect remaining meter-detail fields and transformer fields and
   relationships directly.
7. Check rate-limit behavior only through normal, authorized use and record
   any observed server response; do not infer a limit from a single request.

No API or application behavior is specified or implemented by this protocol
audit.
