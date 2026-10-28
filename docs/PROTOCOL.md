# Urja Meter Ops — Portal and Export Evidence

This document distinguishes facts measured from the local export and the
authenticated portal UI from claims reported by earlier investigation notes.
It does not describe an API integration. No credentials, cookies, or tokens
are recorded here.

## Evidence classifications

- **Verified by direct observation** — seen in the integrated browser during
  this audit. UI observations do not establish the underlying HTTP response
  format or request implementation.
- **Verified by captured request/response or existing test** — supported by a
  retained request/response or a reproducible local test.
- **Inferred but not confirmed** — plausible from the notes or UI, but not
  established by direct evidence available for this audit.
- **Unknown** — not established by available evidence. Earlier notes sometimes
  attribute this gap to lack of portal access; the portal listing was
  accessible in a prior browser observation.

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
  attached to `/meters/J100000`, but navigating to `/meters` ended at the
  sign-in page. The observed navigation chain was `GET /meters` followed by
  `GET /login`; the final `/login` document returned HTTP 200. The status of
  the initial `/meters` response was not captured. This establishes the
  browser's current access state only; it does not establish why the earlier
  signed-in state was no longer present.

### Meter listing visible in the browser

**Verified by direct observation on 2026-10-28:**

- The page was titled **Meters** and displayed **403 total**.
- The table showed 20 records on **Page 1 of 21**. Visible columns were
  `METER`, `SERIAL`, `MAKE`, `PHASE`, `STATUS`, and `DT`.
- Five displayed records were compared with `meter-export.json`. For each of
  `J100000` through `J100004`, `meterId`, `serialNo`, `make`, `phaseType`,
  `installStatus`, and `dtCode` matched the local export exactly.
- This comparison verifies those displayed fields for those five records
  only. It does not validate other fields or prove that the local export and
  portal remain globally identical.

The current observed UI total is **403**, matching the local export. Earlier
notes reporting 405 portal meters are stale or inconsistent with this later
observation; the cause of the earlier count is not established.

The page visibly exposes navigation to Meters, Transformers, Ops Desk, and
Sign out. The Transformers page contents were not examined in this audit.

## 2. Authentication and session behavior

**Verified by direct observation:** The sign-in page at `/login` displayed
Email and Password inputs. The form's declared method is POST, action is
`/login`, and encoding is `application/x-www-form-urlencoded`; its input names
are `email` and `password`. These are form attributes, not a captured
submission. In the earlier signed-in listing observation, the page displayed
a Sign out control.

**Reported by earlier investigation notes, not independently verified in this
audit:** Those notes describe a failed-login JSON response and requests
involving browser headers. The notes conflict on whether successful login was
actually achieved and whether a session cookie was observed. No login
submission was made in this investigation, and no login request/response
capture was available to resolve those conflicts.

**Unknown:** The successful login request and response, exact authentication
mechanism, redirect behavior, whether any additional request headers are
required, and session expiry or revocation behavior. Do not treat the
framework-based cookie explanation in earlier notes as confirmed.

## 3. Portal routes, data requests, and response formats

**Verified by direct observation:** The browser displayed the Meters page at
`/meters`; its navigation included a Transformers link. The sign-in page was
observed at `/login`. In the current browser check, navigation to `/meters`
produced requests for `GET /meters` and then `GET /login`; the final login
document returned HTTP 200.

**Reported by earlier investigation notes, not independently verified here:**
the notes refer to meter-detail and transformer pages and describe their
rendered content. They also report a page-based listing and search/filter UI.
The exact authenticated data-fetching requests, paths, methods, parameters,
request bodies, response schemas, and content types were not captured in
evidence available for this audit. The literal route strings
`/(portal)/meters` and `/(portal)/transformers` in old notes may be
framework-internal route labels; do not assume they are request URLs.

The browser showed rendered table content in the earlier signed-in
observation. This alone does not establish whether the server response was
HTML, JSON, or a combination of page data and client requests. In the current
unauthenticated browser state, no listing, search, pagination, or filter data
requests were observed. No API endpoint or request payload is specified here.

## 4. Local export: verified findings

The following measurements are from the repository's `meter-export.json`, not
from an assumed live API:

- **403 raw records**
- **403 unique, non-null meter IDs**
- **No missing or blank IDs**
- **No duplicate IDs**
- IDs span **J100000–J100402**, with no gaps in that range
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

No separate evidence available in this audit establishes the export button's
request path or whether the local file was produced by the portal's current
export behavior.

## 5. Pagination, filtering, and rate limits

- **Verified by direct observation:** The visible listing reported 403 total
  and Page 1 of 21, showing 20 rows on that page.
- **Reported by earlier notes:** Search by meter number or serial number and
  status options were visible in a prior portal investigation. The exact
  parameters, request behavior, and result counts were not captured here.
- **Current browser limitation:** The listing redirected to the sign-in page,
  so search, pagination, and filtering controls could not be exercised or
  inspected in this investigation.
- **Unknown:** Whether pagination and filtering are performed server-side or
  client-side, the behavior of later pages, exact search/filter controls and
  request parameters, and any rate limits. No rate-limit behavior was tested
  or documented.

## 6. Evidence status by claim

| Claim | Classification | Evidence and limitation |
|---|---|---|
| Local export has 403 records and 403 unique IDs | Verified by direct observation | `meter-export.json`; counts and uniqueness were recalculated |
| IDs are contiguous from J100000 to J100402 | Verified by direct observation | Full numeric interval checked; no gaps |
| Export coordinates are present and valid | Verified by direct observation | All 403 records checked for numeric latitude/longitude ranges |
| Current portal listing shows 403 records and 20 rows on page 1 of 21 | Verified by direct observation | Authenticated browser UI on 2026-10-28 |
| Five portal rows match export values for six visible fields | Verified by direct observation and local comparison | J100000–J100004; no claim about unobserved fields |
| `/meters` showed 502 | Verified by direct observation | Browser event timestamp 2026-10-27 18:34:42.633 UTC |
| Base URL later led to a rendered meter listing | Verified by direct observation | Same shared browser session; 2026-10-28 |
| Current `GET /meters` navigation ends at `GET /login`, final document 200 | Verified by browser navigation | Initial response status was not captured; no login was submitted |
| Login form declares POST `/login` with form encoding and `email`/`password` input names | Verified by direct observation of form attributes | No form submission or request body observed |
| Login is form-based and its failure response has a particular JSON shape | Inferred but not confirmed in this audit | Described in earlier notes; no request/response capture available here |
| A successful login sets a session cookie | Inferred but not confirmed | Earlier notes conflict; no login response or cookie was inspected |
| Session expiration behavior | Unknown | Not observed or tested |
| Exact authenticated data-fetching endpoints and response schemas | Unknown | Current browser redirected to login; no authenticated request/response capture available |
| Portal detail and transformer data fields | Unknown | Not inspected in this audit |
| 405 portal records | Not supported by the current observation | Earlier notes report 405; current listing reports 403 |

## 7. Earlier investigation notes and limitations

`docs/PHASE1_INVESTIGATION.md`, `docs/API_DESIGN.md`, `README.md`,
`Final_Report.md`, `BLOCKER_REPORT.md`, `AUDIT_OUTPUT.md`, and
`audit_output.txt` contain historical claims. They are not independent
evidence by themselves. In particular:

- Some notes label authentication details as verified while also saying that
  valid credentials or successful authenticated access were unavailable.
- The notes disagree on the portal count (405 versus 403) and on the evidence
  for successful authentication.
- Proposed API endpoints in API design documents describe a proposed service,
  not confirmed portal endpoints.
- Local application test results verify the local API against the export; they
  do not prove live portal protocol behavior.

Claims should be promoted to verified status only when supported by a
reproducible capture or a directly observed portal result with its scope
recorded.

## 8. Checks still required

The meter listing was accessible in an earlier shared browser session, but the
current browser check ended at the sign-in page. The following protocol
details remain unverified:

1. When the authorized session is available, capture the login flow's actual
   request and response without recording credentials or session material;
   verify redirect and successful authentication behavior. Do not submit
   credentials unless the user performs or authorizes the normal login flow.
2. Observe the actual data-fetching requests for listing, meter details,
   transformer data, and export. Record paths, methods, parameters, status
   codes, content types, and sanitized response shapes; do not guess endpoints.
3. Exercise pagination and search/status filters and compare returned results
   with what the UI displays.
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
6. Inspect transformer and meter-detail fields and their hierarchy
   relationships directly.
7. Check rate-limit behavior only through normal, authorized use and record
   any observed server response; do not infer a limit from a single request.

No API or application behavior is specified or implemented by this protocol
audit.
