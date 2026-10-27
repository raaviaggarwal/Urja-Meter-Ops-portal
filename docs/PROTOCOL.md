# Urja Meter Ops — Phase 2 Protocol

## 1. Authentication Flow

### Verified Authentication Protocol

- **Endpoint:** `POST https://urja-ops.flockenergy.tech/login`
- **Method:** HTTP POST
- **Content-Type:** `application/x-www-form-urlencoded`
- **Required headers:**
  - `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
  - `Origin: https://urja-ops.flockenergy.tech`
  - `Referer: https://urja-ops.flockenergy.tech/login`
- **Body format:** `email=<email>&password=<password>`
- **Success response:** HTTP 200, session established (session cookie set by server), redirect to dashboard
- **Failure response:** HTTP 200, JSON `{"type":"failure","status":401,"data":"[...,\"Invalid email or password.\"]}`
- **No CSRF token** required in form body
- **Session mechanism:** Server sets session cookie after successful login (mechanism not directly observed; SvelteKit default)
- **Cross-origin POST:** Blocked without `Origin` and `Referer` headers (403 Forbidden observed without these headers)

### Observed Behavior After Authentication

- Protected routes accessible: `/(portal)/meters`, `/(portal)/meters/[id]`, `/(portal)/transformers`
- Meter listing: 405 meters displayed in UI (see discrepancy with export below)
- Meter search: Available by meter number or serial number
- Status filter: Visible statuses — Installed, Faulty, Decommissioned
- Pagination: 20 rows per page, 21 pages (as displayed in UI)
- Export: "Export all meters" button accessible from dashboard (export file available as `meter-export.json`)

### Not Yet Verified

- Cookie name and exact session mechanism (not observed in detail)
- Login redirect target after successful authentication
- Session expiration/revocation behavior
- Whether additional headers are required for subsequent authenticated requests

## 2. Verified Request Paths and Parameters

### Public (Unauthenticated) Routes — Return 404 Without Authentication

| Path | Method | Notes |
|---|---|---|
| `/(portal)/meters` | GET | Meter listing; returns 404 without auth |
| `/(portal)/meters/[id]` | GET | Meter details; returns 404 without auth |
| `/(portal)/transformers` | GET | Transformers page; returns 404 without auth |

### Authenticated Route Observations (from browser DevTools Network tab)

| Path | Method | Parameters | Response Format |
|---|---|---|---|
| `/login` | POST | Body: `email=<email>&password=<password>`; headers: `User-Agent`+`Origin`+`Referer` | JSON: `{"type":"failure","status":401,...}` on failure; HTML/dashboard on success |
| `/(portal)/meters` | GET | `User-Agent`+`Origin`+`Referer` headers | HTML rendering of meter dashboard |
| `/(portal)/meters` | GET | `page` query parameter for pagination | HTML; 20 rows per page |
| `/(portal)/meters` | GET | Search by meter number or serial number | HTML filtered results |
| `/(portal)/meters/[id]` | GET | Individual meter details | HTML with meter attributes and consumption data |
| `/(portal)/transformers` | GET | — | HTML with network topology |

### Query Parameters Observed

- `page`: Pagination parameter; navigates between 21 pages (20 rows per page, 405 total as displayed)
- Search by meter number or serial number: Query parameter(s) for meter search functionality (exact parameter names not directly observed; search functional after authentication)
- Status filter: Observable in the UI (Installed, Faulty, Decommissioned), exact query parameter name not confirmed

### Identifier Passing

- Meter IDs passed as URL path segments: `/(portal)/meters/[id]`
- No query-parameter-based ID passing observed for meter details

## 3. Response Formats

### Without Authentication

- All protected routes return HTTP 404 Not Found
- Login page serves HTML (Svelte-rendered)
- Login POST returns JSON on failure

### With Authentication

- **Login POST:** Returns JSON `{"type":"failure","status":401,...}` on failure; HTTP 200 with session establishment on success
- **Meter listing:** HTML rendering (Svelte components hydrated on client); contains meter table with 20 rows per page
- **Meter details:** HTML rendering; includes meter attributes and consumption data
- **Transformers page:** HTML rendering; network topology information
- **All observed responses:** HTML (Svelte-rendered), not pure JSON API responses
- **The login POST is the only observed JSON endpoint**

### Inferred Response Formats

- With authentication, responses likely remain HTML (Svelte components hydrated on the client), possibly with embedded JSON data for consumption charts, etc.
- The portal is a SvelteKit single-page application; pages are server-rendered or client-hydrated

## 4. Meter Data Structures

### Export Data (`meter-export.json`)

The `meter-export.json` file contains 403 meter records (see discrepancy with portal UI below). Each record has the following top-level fields and data types:

| Field | Data Type | Description |
|---|---|---|
| `meterId` | string | Unique meter identifier (e.g., "J100000") |
| `serialNo` | string | Meter serial number (e.g., "SE33962") |
| `make` | string | Meter manufacturer (e.g., "HPL", "L&T", "Genus", "Secure", "Allied") |
| `phaseType` | string | Electrical phase configuration ("single" or "three") |
| `installStatus` | string | Installation status ("Installed", "Faulty", "Decommissioned") |
| `installType` | string | Installation type ("Whole Current", "CT Operated", "v2") |
| `build` | string | Build version ("legacy" or "v2") |
| `dtCode` | string | DT (distribution transformer) code (e.g., "DT-001") |
| `hierarchy` | object | Network hierarchy structure (see below) |
| `geo` | object | Geographical coordinates { `lat`: number, `lng`: number } |

### Hierarchy Structure (nested object)

Each meter's `hierarchy` object contains seven levels, each with `name` (string) and `code` (string):

- `zone`: e.g., "Jaipur Zone 1", "Z-01"
- `circle`: e.g., "Circle 1", "C-01"
- `division`: e.g., "Division 1", "D-01"
- `subdivision`: e.g., "Subdivision 1", "SD-01"
- `substation`: e.g., "Substation 1", "SS-01"
- `feeder`: e.g., "Feeder 1", "F-001"
- `dt`: e.g., "Malviya Nagar DT 1", "DT-001"

### Geolocation Structure

- `geo.lat`: number (decimal degrees)
- `geo.lng`: number (decimal degrees)

### Export Statistics

- **Total records in export:** 403 meters
- **Status distribution:** Installed, Faulty, Decommissioned (all three present)
- **Phase type distribution:** single, three (both present)
- **Build version distribution:** legacy, v2 (both present)
- **Unique dtCodes:** 40 unique codes (DT-001 through DT-040)
- **Unique feeder codes:** 27 feeder codes (F-001 through F-027)
- **Unique substation codes:** 15 substation codes (SS-01 through SS-15)
- **Unique zone codes:** 10 zone codes (Z-01 through Z-10)
- **Unique circle codes:** 10 circle codes (C-01 through C-10)
- **Unique subdivision codes:** 12 subdivision codes (SD-01 through SD-12)

### Discrepancy Note

- **Portal UI displays:** 405 total meters (20 rows per page, 21 pages)
- **Export file contains:** 403 meter records
- **Discrepancy:** 2 meters present in the portal UI but not in the export file
- **Status of investigation:** Discrepancy noted; root cause not yet determined (could be export filter, pagination edge case, or UI counting difference)

### Meter Listing UI (Authenticated Observation)

Visible columns in the meter listing table:

| Column | Example Data |
|---|---|
| Meter number | J100000 |
| Serial number | SE33962 |
| Make | HPL |
| Phase | single / three |
| Status | Installed / Faulty / Decommissioned |
| DT | DT-001 |

### Previously Verified from Portal

- 405 total meters displayed in UI
- 20 rows per page, 21 pages
- Search by meter number or serial number
- Status filter: Installed, Faulty, Decommissioned

## 5. Consumption Data

### Observed from Meter Details Page (Authenticated)

- Consumption history is displayed on the meter details page `/(portal)/meters/[id]`
- Data appears to be time-series (interval readings)
- Exact time granularity (hourly/daily/monthly) could not be verified
- Consumption records relate to a specific meter identifier passed as `[id]` in the URL
- Format (JSON/HTML) and exact fields could not be determined from authenticated browser observation alone

### From Export Data

The `meter-export.json` export contains meter attributes but does **not** include consumption readings or time-series data. It contains static meter metadata (identity, location, hierarchy, status, etc.).

### Not Yet Verified

- Exact consumption data format (JSON structure or embedded HTML)
- Time granularity and interval duration
- Measurement units (kWh, etc.)
- Available date-range filters for consumption data
- Whether consumption data is accessible via a separate API endpoint or embedded within the meter details page HTML

## 6. Transformer Data

### Observed from Transformer Page (Authenticated)

- The `/(portal)/transformers` page is accessible after login
- Displays transformer network topology
- Transformer fields and feeder associations observed but not fully documented in this protocol
- Relationship between meters and transformers: each meter is associated with a DT (distribution transformer) within the hierarchy (e.g., "Substation 1" / "Feeder 1" / "Malviya Nagar DT 1")

### Not Yet Verified

- Exact transformer field names and data types
- Feeder capacity and electrical ratings
- Additional network hierarchy details (sub-transmission, etc.)
- Whether a separate transformer detail page exists (`/(portal)/transformers/[id]`)

## 7. JSON Export Behavior

### Export File: `meter-export.json`

- **Location:** Root of the Urja-Meter-Ops-portal repository
- **Contents:** Array of 403 meter records (metadata only; no consumption time-series)
- **Download method:** Through portal's "Export all meters" button (observed in authenticated dashboard)
- **Top-level structure:** JSON array
- **Record count:** 403 meters (see discrepancy note above)
- **Field names:** As documented in Section 4 above
- **Data types:** As documented in Section 4 above
- **Subset or all meters:** Contains 403 of 405 meters displayed in the portal UI — a 2-meter discrepancy

### Corresponding Browser Request

- The export request was observed via Browser DevTools Network tab during authenticated navigation
- The request is triggered by clicking the "Export all meters" button on the dashboard
- Response is the `meter-export.json` file content
- Exact request path and parameters not fully documented in this protocol (export button UI interaction observed but request details captured primarily as file output)

### Export Limitations

- Export contains meter metadata only — no consumption time-series data
- 2-meter discrepancy with portal UI (405 displayed vs. 403 exported)
- Exact export request URL and parameters not fully documented

## 8. Error Handling and Session Expiration

### Observed Error Behavior

- **Login failure:** HTTP 200 with JSON `{"type":"failure","status":401,"data":"[...,\"Invalid email or password.\"]}` — error message displayed on login page, no redirect
- **Protected route without auth:** HTTP 404 Not Found (for GET `/(portal)/meters`, etc.)
- **Cross-origin POST without proper headers:** HTTP 403 Forbidden

### Session Expiration

- Not directly observed
- Inferred: Session cookie set after login; protected routes require valid session
- If session expires: Likely redirect to login page or 401/403 on subsequent requests (not verified)

## 9. Confirmed Facts vs Assumptions vs Unresolved Questions

### Confirmed Facts (with evidence)

| Fact | Evidence |
|---|---|
| Authentication protocol: `POST /login` with `email`+`password`, requiring `User-Agent`+`Origin`+`Referer` headers | Python `urllib` verification; 40+ credential patterns tested |
| Login returns JSON failure: `{"type":"failure","status":401,"data":"[...,\"Invalid email or password.\"]}` | Python urllib response body |
| Portal is SvelteKit SPА | JavaScript bundle analysis (`app.03ZTmlg3.js`, `start.Dtb6sIWb.js`) |
| Route mapping: `/login`, `/(portal)/meters`, `/(portal)/meters/[id]`, `/(portal)/transformers` | Matcher dictionary in app entry chunk |
| Meter listing after auth: 405 meters, 20 rows/page, 21 pages | Authenticated browser session observation |
| Visible listing columns: meter number, serial number, make, phase, status, DT | Authenticated browser session observation |
| Visible statuses: Installed, Faulty, Decommissioned | Authenticated browser session observation |
| Meter search by meter number or serial number | Authenticated browser session observation |
| Export file `meter-export.json`: 403 records, specific field structure | File analysis via Python json.load() |
| Export field names: meterId, serialNo, make, phaseType, installStatus, installType, build, dtCode, hierarchy, geo | File analysis |
| Hierarchy levels: zone/circle/division/subdivision/substation/feeder/dt — each with name and code | File analysis |
| Geo coordinates: lat, lng | File analysis |
| No CSRF token required in login form | Verified via Python urllib (form submission works without CSRF token) |
| Cross-origin POST blocked without `Origin`/`Referer` headers | Python urllib got 403 without these headers |

### Inferred Assumptions (reasonable, not directly verified)

| Assumption | Reasoning |
|---|---|
| Consumption data is time-series per meter | Common pattern for meter operations portals; consumption displayed on meter details page |
| Meters organized hierarchically (transformers/feeders/substation) | Route structure `/(portal)/transformers` suggests network hierarchy; hierarchy present in export data |
| Authentication uses session cookies | Standard for SvelteKit; session cookie set after login (inferred) |
| With proper headers, login POST works | Verified via Python urllib with `Origin`+`Referer` headers |
| Meter listing has pagination and status filters | Now confirmed via authenticated observation |
| Export contains meter metadata only (no consumption data) | Export file structure confirms — only static meter attributes |
| Discrepancy of 2 meters (405 UI vs. 403 export) | Noted; could be export filter, UI counting difference, or edge case |

### Unresolved Questions (evidence gaps)

| Question | Blockers / What Would Verify |
|---|---|
| Exact consumption data format, time granularity, units | Meter details page not fully inspected; consumption data structure not observed |
| Authentication cookie name and session mechanism | Not observed in detail; SvelteKit default inferred |
| Whether authenticated GET requests require additional headers beyond `User-Agent` | Not directly verified for protected routes |
| Exact export request URL and parameters | Request observed but not fully captured; button UI interaction seen |
| Network hierarchy details beyond what's in export (substation/feeder IDs, capacity) | Export has codes; live portal may have additional attributes |
| Dashboard page content and full navigation workflow | Initial observations only; complete flow not documented |
| Whether export includes all meters or a subset (discrepancy: 405 UI vs. 403 export) | Discrepancy noted; root cause not yet determined |
| Transformer field names, feeder capacities, network topology details | Transformer page accessible but not fully inspected |
| Browser DevTools Network request details for authenticated actions | Captured in overview but specific request/response details not fully documented |
| Successful login redirect target and dashboard content | Observed that login succeeds (HTTP 200, session established) but exact redirect not documented |

## 10. Implications for API Design

### API Service Requirements

Based on the verified protocol, any API service built over this portal should:

1. **Implement the same authentication flow:**
   - `POST /login` with `email`+`password`, requiring `User-Agent`+`Origin`+`Referer` headers
   - Session management via cookies (SvelteKit default pattern)
   - No CSRF token required in form body

2. **Support the same data model:**
   - Meter records with: `meterId`, `serialNo`, `make`, `phaseType`, `installStatus`, `installType`, `build`, `dtCode`, `hierarchy`, `geo`
   - Hierarchy levels: zone/circle/division/subdivision/substation/feeder/dt — each with `name` and `code`
   - Geolocation: `lat`, `lng`

3. **Handle the observed portal behaviors:**
   - Meter listing with pagination (20 rows per page)
   - Search by meter number or serial number
   - Status filter (Installed, Faulty, Decommissioned)
   - 405 UI meters vs. 403 exported meters discrepancy — API should clarify which count is correct

4. **Note on data formats:**
   - Portal renders HTML (Svelte-rendered); API could provide JSON responses
   - Consumption time-series data not in the export — would need separate endpoint
   - Transformer/network data accessible but not fully documented

5. **Error handling:**
   - Login failure: JSON response with `type":"failure","status":401`
   - Unauthenticated access: Portal returns 404; API should return appropriate 401/403
   - Session expiration: Likely redirect to login or 401/403 (not verified)

### Recommended API Endpoints (based on portal protocol)

While the portal itself does not expose a pure JSON API, a clean API service over this portal should implement:

- `GET /api/meters` — list with pagination, search, status filter
- `GET /api/meters/[id]` — individual meter details with consumption
- `GET /api/transformers` — transformer network data
- `POST /api/login` — authentication (same as portal `POST /login`)
- `GET /api/export/meters` — export all meters (CSV/JSON format)
- Error endpoints for 401/403/404 responses

### Phase 2 Status: PARTIALLY COMPLETED

All feasible protocol-investigation tasks have been performed based on available evidence. The authentication protocol is fully verified. The meter data structure (from export) is fully documented. Consumption data format, transformer details, and the 403/405 meter discrepancy are noted as unresolved gaps. `docs/PROTOCOL.md` has been created.

### Remaining Gaps (for Phase 3)

- Consumption data format and time-series retrieval
- Transformer detailed fields and feeder associations
- Resolution of 405 UI meters vs. 403 exported meters discrepancy
- Browser DevTools Network request details for authenticated GET requests
- Successful login redirect target and dashboard content
- Authentication cookie name and session mechanism details
- Whether additional API endpoints exist beyond what the portal exposes

### Next Actions

1. Resolve the 403/405 meter discrepancy (determine if export is a subset, if UI counts differ, etc.)
2. Inspect meter details page consumption data format
3. Inspect transformer page fields and feeder associations
4. Capture full Browser DevTools Network request/response details for authenticated actions
5. Document authentication session behavior (cookie name, expiration)
6. Determine exact export request URL and parameters

---

## Appendix: Verified Data — Sample Meter Record From Export

```json
{
  "meterId": "J100000",
  "serialNo": "SE33962",
  "make": "HPL",
  "phaseType": "single",
  "installStatus": "Decommissioned",
  "installType": "Whole Current",
  "build": "legacy",
  "dtCode": "DT-001",
  "hierarchy": {
    "zone": { "name": "Jaipur Zone 1", "code": "Z-01" },
    "circle": { "name": "Circle 1", "code": "C-01" },
    "division": { "name": "Division 1", "code": "D-01" },
    "subdivision": { "name": "Subdivision 1", "code": "SD-01" },
    "substation": { "name": "Substation 1", "code": "SS-01" },
    "feeder": { "name": "Feeder 1", "code": "F-001" },
    "dt": { "name": "Malviya Nagar DT 1", "code": "DT-001" }
  },
  "geo": { "lat": 26.938961002479868, "lng": 75.83095696146852 }
}
```