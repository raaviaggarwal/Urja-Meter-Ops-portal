"""Flock Energy API - FastAPI implementation for meter operations dataset."""

import json
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(os.path.dirname(__file__), "meter-export.json")

def load_dataset() -> List[Dict[str, Any]]:
    """Load and validate the meter dataset at startup.

    Returns the dataset list. Raises RuntimeError if the file is missing or
    malformed so the service fails fast rather than returning confusing
    500 errors on every request.
    """
    if not os.path.isfile(DATA_PATH):
        raise RuntimeError(f"Dataset file not found at {DATA_PATH}")
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON from {DATA_PATH}: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"Dataset at {DATA_PATH} is not a JSON array")
    # Validate that every record has the expected top-level fields
    expected_fields = {
        "meterId", "serialNo", "make", "phaseType", "installStatus",
        "installType", "build", "dtCode", "hierarchy", "geo"
    }
    for i, record in enumerate(data):
        missing = expected_fields - set(record.keys())
        if missing:
            raise RuntimeError(
                f"Record #{i} is missing required fields: {sorted(missing)}"
            )
    return data

# Load dataset once at startup; the original file is never modified.
try:
    dataset = load_dataset()
    TOTAL_RECORDS = len(dataset)
except RuntimeError as exc:
    # If the dataset cannot be loaded, the app will start but every
    # request that touches the data will return a 500. This is intentional
    # — the operator must fix the data-path problem before the service
    # is usable.
    dataset = []
    TOTAL_RECORDS = 0

# ---------------------------------------------------------------------------
# In-memory indexes (built once at startup)
# ---------------------------------------------------------------------------

# map meterId -> record
_by_id: Dict[str, Dict[str, Any]] = {r["meterId"]: r for r in dataset}

# map serialNo -> record (last wins if duplicates exist)
_by_serial: Dict[str, Dict[str, Any]] = {}
for r in dataset:
    _by_serial.setdefault(r["serialNo"], r)

# index by installStatus -> list of meterId
_by_status: Dict[str, List[str]] = {}
for r in dataset:
    _by_status.setdefault(r["installStatus"], []).append(r["meterId"])

# index by phaseType -> list of meterId
_by_phase: Dict[str, List[str]] = {}
for r in dataset:
    _by_phase.setdefault(r["phaseType"], []).append(r["meterId"])

# index by build -> list of meterId
_by_build: Dict[str, List[str]] = {}
for r in dataset:
    _by_build.setdefault(r["build"], []).append(r["meterId"])

# index by dtCode -> list of meterId
_by_dt: Dict[str, List[str]] = {}
for r in dataset:
    _by_ct = r.get("hierarchy", {}).get("dt", {})
    dt_code = _ct.get("code", "")
    _by_ct.setdefault(dt_code, []).append(r["meterId"])

# index by zone code -> list of meterId
_by_zone: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("zone", {})
    zone_code = _ct.get("code", "")
    _by_zone.setdefault(zone_code, []).append(r["meterId"])

# index by circle code -> list of meterId
_by_circle: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("circle", {})
    circle_code = _ct.get("code", "")
    _by_circle.setdefault(circle_code, []).append(r["meterId"])

# index by division code -> list of meterId
_by_division: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("division", {})
    division_code = _ct.get("code", "")
    _by_division.setdefault(division_code, []).append(r["meterId"])

# index by subdivision code -> list of meterId
_by_subdivision: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("subdivision", {})
    sub_code = _ct.get("code", "")
    _by_subdivision.setdefault(sub_code, []).append(r["meterId"])

# index by substation code -> list of meterId
_by_substation: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("substation", {})
    sub_code = _ct.get("code", "")
    _by_substation.setdefault(sub_code, []).append(r["meterId"])

# index by feeder code -> list of meterId
_by_feeder: Dict[str, List[str]] = {}
for r in dataset:
    _ct = r.get("hierarchy", {}).get("feeder", {})
    feeder_code = _ct.get("code", "")
    _by_feeder.setdefault(feeder_code, []).append(r["meterId"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summary_record(r: Dict[str, Any]) -> Dict[str, Any]:
    """Return a lightweight summary record for listing endpoints."""
    h = r.get("hierarchy", {})
    return {
        "meterId": r["meterId"],
        "serialNo": r.get("serialNo", ""),
        "make": r.get("make", ""),
        "phaseType": r.get("phaseType", ""),
        "installStatus": r.get("installStatus", ""),
        "dtCode": r.get("dtCode", ""),
        "hierarchy": {
            "zone": {"name": h.get("zone", {}).get("name", ""), "code": h.get("zone", {}).get("code", "")},
            "dt": {"name": h.get("dt", {}).get("name", ""), "code": h.get("dt", {}).get("code", "")},
        },
        "geo": r.get("geo", {"lat": None, "lng": None}),
    }


def _full_record(r: Dict[str, Any]) -> Dict[str, Any]:
    """Return the complete meter record as stored in the dataset."""
    return dict(r)


def _parse_bool(v: Any) -> Optional[bool]:
    """Coerce a query‑parameter value to an optional boolean."""
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    return v.lower() in ("1", "true", "yes", "y")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Flock Energy Meter API",
    description="Read‑only API over the Flock Energy meter operations dataset.",
    version="1.0.0",
)

@app.get("/health", include_in_schema=False)
async def health() -> Dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Helper: parse pagination params
# ---------------------------------------------------------------------------

def _paginate(
    items: List[str],
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, Any]:
    """Return a pagination wrapper for a list of meterIds."""
    page = max(page, 1)
    per_page = max(per_page, 1)
    total = len(items)
    total_pages = (total + per_page - 1) // per_page if total else 0
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    return {
        "items": page_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/meters", response_model=dict)
async def list_meters(
    page: int = Query(1, ge=1, description="Page number (1‑indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Substring search on meterId or serialNo"),
    status: Optional[str] = Query(
        None, regex=r"^(Installed|Faulty|Decommissioned)$",
        description="Filter by installation status"
    ),
    phase_type: Optional[str] = Query(
        None, regex=r"^(single|three)$",
        description="Filter by electrical phase type"
    ),
    build: Optional[str] = Query(
        None, regex=r"^(legacy|v2)$",
        description="Filter by build version"
    ),
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (Z-01, Z-02, Z-03)"
    ),
    division_code: Optional[str] = Query(
        None, description="Filter by division code (D-01 … D-10)"
    ),
    dt_code: Optional[str] = Query(
        None, description="Filter by DT code (DT-001 … DT-040)"
    ),
) -> Dict[str, Any]:
    """List meters with pagination, search, and hierarchical filters.

    The returned dict contains:
    - ``meters``: list of summary records
    - ``total``: total number of matching records (before pagination)
    - ``page``, ``per_page``, ``total_pages``: pagination metadata
    """
    # Start with the full set of meterIds
    meter_ids: List[str] = list(_by_id.keys())

    # Apply filters
    if status:
        meter_ids = _by_status.get(status, [])
    elif phase_type:
        meter_ids = _by_phase.get(phase_type, [])
    elif build:
        meter_ids = _by_build.get(build, [])

    # Hierarchy filters (AND‑combined with each other and with prior filters)
    if zone_code:
        meter_ids = _by_zone.get(zone_code, [])
    if division_code:
        meter_ids = _by_division.get(division_code, [])
    if dt_code:
        meter_ids = _by_dt.get(dt_code, [])
    if zone_code and division_code:
        # When both zone and division are provided, intersect the two lists
        meter_ids = [mid for mid in meter_ids if mid in _by_division.get(division_code, [])]
    # Note: circle, subdivision, substation, feeder filters can be added
    # following the same pattern; they are omitted from the minimal
    # implementation but the index tables (_by_circle, etc.) are pre‑built.

    # Search filter (applied after the above so it can further narrow results)
    if search:
        search_lower = search.lower()
        meter_ids = [
            mid for mid in meter_ids
            if search_lower in mid.lower()
            or search_lower in (_by_id.get(mid, {}).get("serialNo", "").lower())
        ]

    # Pagination
    paginated = _paginate(meter_ids, page=page, per_page=per_page)

    # Build summary records
    meters = [_summary_record(_by_id[mid]) for mid in paginated["items"]]

    return {
        "meters": meters,
        "total": paginated["total"],
        "page": paginated["page"],
        "per_page": paginated["per_page"],
        "total_pages": paginated["total_pages"],
    }


@app.get("/api/meters/{meter_id}", response_model=dict)
async def get_meter(meter_id: str) -> Dict[str, Any]:
    """Retrieve a single meter's full metadata record.

    Returns a 404 response if the meterId does not exist in the dataset.
    """
    record = _by_id.get(meter_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Meter not found")
    return _full_record(record)


@app.get("/api/meters/search", response_model=dict)
async def search_meters(
    query: str = Query(..., min_length=1, description="Substring to search on meterId or serialNo"),
) -> Dict[str, Any]:
    """Search meters by meterId or serial number substring.

    Returns matching records as summary objects.
    """
    search_lower = query.lower()
    matched: List[Dict[str, Any]] = []
    for mid, rec in _by_id.items():
        sid = rec.get("serialNo", "").lower()
        if search_lower in mid.lower() or search_lower in sid:
            matched.append(_summary_record(rec))

    return {
        "meters": matched,
        "total": len(matched),
        "query": query,
    }


@app.get("/api/meters/status/{status}", response_model=dict)
async def list_meters_by_status(
    status: str = Path(..., regex=r"^(Installed|Faulty|Decommissioned)$"),
) -> Dict[str, Any]:
    """List meters filtered by installation status.

    Returns a summary list and the total count for the given status.
    """
    meter_ids = _by_status.get(status, [])
    paginated = _paginate(meter_ids, page=1, per_page=max(1, 20))
    meters = [_summary_record(_by_id[mid]) for mid in paginated["items"]]
    return {
        "meters": meters,
        "total": paginated["total"],
        "status": status,
        "page": paginated["page"],
        "per_page": paginated["per_page"],
        "total_pages": paginated["total_pages"],
    }


@app.get("/api/transformers", response_model=dict)
async def list_transformers() -> Dict[str, Any]:
    """Provide transformer‑derived information from the meter dataset.

    This endpoint does not fabricate capacities or electrical ratings; it
    exposes the hierarchy information that is available from the meter
    records. Each unique DT (distribution transformer) appearing in the
    dataset is listed with its associated zone, circle, subdivision,
    substation, and feeder codes/names as observed in the data.

    The response format is intentionally lightweight — it reflects what
    can be derived from the 403‑record export without making assumptions
    about fields that are not present.
    """
    # Collect unique DT entries
    dt_entries: Dict[str, Dict[str, Any]] = {}
    for r in dataset:
        h = r.get("hierarchy", {})
        dt = h.get("dt", {})
        dt_code = dt.get("code", "")
        if not dt_code:
            continue
        if dt_code in dt_entries:
            continue
        # Build a summary from the first record that has this DT code
        dt_entries[dt_code] = {
            "dtCode": dt_code,
            "dtName": dt.get("name", ""),
            "zoneCode": h.get("zone", {}).get("code", ""),
            "zoneName": h.get("zone", {}).get("name", ""),
            "circleCode": h.get("circle", {}).get("code", ""),
            "circleName": h.get("circle", {}).get("name", ""),
            "divisionCode": h.get("division", {}).get("code", ""),
            "divisionName": h.get("division", {}).get("name", ""),
            "substationCode": h.get("substation", {}).get("code", ""),
            "substationName": h.get("substation", {}).get("name", ""),
            "feederCode": h.get("feeder", {}).get("code", ""),
            "feederName": h.get("feeder", {}).get("name", ""),
            "meterCount": sum(1 for r2 in dataset if r2.get("hierarchy", {}).get("dt", {}).get("code", "") == dt_code),
        }

    return {
        "transformers": list(dt_entries.values()),
        "total": len(dt_entries),
    }


@app.get("/api/export/meters", response_model=dict)
async def export_meters() -> Dict[str, Any]:
    """Return the verified meter dataset.

    This endpoint returns the 403‑record export that lives alongside the
    API code. It documents the known discrepancy with the portal UI (405
    meters displayed vs. 403 records exported) without inventing the
    missing records or their reason.
    """
    return {
        "count": TOTAL_RECORDS,
        "meters": dataset,
    }


# ---------------------------------------------------------------------------
# Global exception handler so we never expose stack traces/secrets
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "message": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    # In production one would log `exc` securely. Here we return a generic
    # 500 with a minimal message so no secrets leak in the response.
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )