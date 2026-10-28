"""Flock Energy API - FastAPI implementation for meter operations dataset."""

import json
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Path, Query
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
    dt_code = r.get("dtCode", "")
    _by_dt.setdefault(dt_code, []).append(r["meterId"])

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
# Metadata endpoint
# ---------------------------------------------------------------------------

@app.get("/api/metadata", response_model=dict)
async def get_metadata() -> Dict[str, Any]:
    """Get data source metadata and freshness information.

    Returns metadata about the meter dataset including:
    - Record count
    - Source filename
    - File modification time (local file system metadata)
    - Freshness policy

    This endpoint does not connect to the live portal and does not
    provide real-time data. All data comes from the static export
    file meter-export.json alongside the API code.
    """
    import datetime
    file_path = os.path.join(os.path.dirname(__file__), "meter-export.json")
    stat = os.stat(file_path)
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
    return {
        "record_count": TOTAL_RECORDS,
        "source_file": "meter-export.json",
        "file_modification_time": mtime.isoformat(),
        "freshness": {
            "policy": "static_export",
            "description": "Data comes from a static export file; no live portal connection.",
            "last_updated": None
        },
        "dataset": {
            "phase_types": list(set(r.get("phaseType") for r in dataset)),
            "statuses": list(set(r.get("installStatus") for r in dataset)),
            "makes": list(set(r.get("make") for r in dataset)),
        }
    }


# ---------------------------------------------------------------------------
# Nearby meters endpoint (Haversine formula)
# ---------------------------------------------------------------------------

@app.get("/api/meters/nearby", response_model=dict)
async def nearby_meters(
    latitude: float = Query(..., description="Latitude in decimal degrees, -90 to 90"),
    longitude: float = Query(..., description="Longitude in decimal degrees, -180 to 180"),
    radius_km: float = Query(..., gt=0, le=500, description="Search radius in kilometres"),
) -> Dict[str, Any]:
    """Find meters near a given location using the Haversine formula.

    Parameters:
    - latitude: Latitude in decimal degrees (-90 to 90)
    - longitude: Longitude in decimal degrees (-180 to 180)
    - radius_km: Search radius in kilometres (maximum 500)

    Returns meters sorted by ascending distance with their distance in km.
    Results with missing or nil coordinates are silently skipped.
    """
    import math
    if not -90 <= latitude <= 90:
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")

    R = 6371  # Earth radius in kilometres
    results = []

    for r in dataset:
        geo = r.get("geo")
        if geo is None or geo.get("lat") is None or geo.get("lng") is None:
            continue
        lat1 = math.radians(latitude)
        lng1 = math.radians(longitude)
        lat2 = math.radians(geo["lat"])
        lng2 = math.radians(geo["lng"])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        if distance <= radius_km:
            results.append(
                {"meterId": r["meterId"], "distance_km": round(distance, 4)}
            )

    results.sort(key=lambda x: x["distance_km"])
    return {"meters": results, "total": len(results)}


# ---------------------------------------------------------------------------
# Hierarchy endpoint
# ---------------------------------------------------------------------------

def _build_hierarchy(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a tree representing the meter network hierarchy.

    Returns a nested dict with zones → circles → divisions → subdivisions
    → substations → feeders → distribution transformers, each with meter
    counts and sample meterIds.  Empty hierarchy codes are preserved with
    a special marker so callers can distinguish "no code" from "absent level".
    """
    # Initialise empty nested structure
    hierarchy: Dict[str, Any] = {
        "zones": {},
        "total_records": len(dataset),
    }

    for r in dataset:
        h = r.get("hierarchy", {})
        zone_name = h.get("zone", {}).get("name", "")
        zone_code = h.get("zone", {}).get("code", "")
        circle_name = h.get("circle", {}).get("name", "")
        circle_code = h.get("circle", {}).get("code", "")
        division_name = h.get("division", {}).get("name", "")
        division_code = h.get("division", {}).get("code", "")
        subdivision_name = h.get("subdivision", {}).get("name", "")
        subdivision_code = h.get("subdivision", {}).get("code", "")
        substation_name = h.get("substation", {}).get("name", "")
        substation_code = h.get("substation", {}).get("code", "")
        feeder_name = h.get("feeder", {}).get("name", "")
        feeder_code = h.get("feeder", {}).get("code", "")
        dt_name = h.get("dt", {}).get("name", "")
        dt_code = h.get("dt", {}).get("code", "")
        meter_id = r.get("meterId", "")

        # --- zone ---
        if zone_name not in hierarchy["zones"]:
            hierarchy["zones"][zone_name] = {
                "code": zone_code,
                "circles": {},
            }
        zone = hierarchy["zones"][zone_name]

        # --- circle ---
        circle_key = circle_name if circle_code else f"_empty_code_{circle_name}"
        if circle_key not in zone["circles"]:
            zone["circles"][circle_key] = {
                "name": circle_name,
                "code": circle_code,
                "divisions": {},
            }
        circle = zone["circles"][circle_key]

        # --- division ---
        div_key = division_name if division_code else f"_empty_code_{division_name}"
        if div_key not in circle["divisions"]:
            circle["divisions"][div_key] = {
                "name": division_name,
                "code": division_code,
                "subdivisions": {},
            }
        division = circle["divisions"][div_key]

        # --- subdivision ---
        sub_key = subdivision_name if subdivision_code else f"_empty_code_{subdivision_name}"
        if sub_key not in division["subdivisions"]:
            division["subdivisions"][sub_key] = {
                "name": subdivision_name,
                "code": subdivision_code,
                "substations": {},
            }
        subdivision = division["subdivisions"][sub_key]

        # --- substation ---
        sub_key2 = substation_name if substation_code else f"_empty_code_{substation_name}"
        if sub_key2 not in subdivision["substations"]:
            subdivision["substations"][sub_key2] = {
                "name": substation_name,
                "code": substation_code,
                "feeders": {},
            }
        substation = subdivision["substations"][sub_key2]

        # --- feeder ---
        feed_key = feeder_name if feeder_code else f"_empty_code_{feeder_name}"
        if feed_key not in substation["feeders"]:
            substation["feeders"][feed_key] = {
                "name": feeder_name,
                "code": feeder_code,
                "dts": {},
            }
        feeder = substation["feeders"][feed_key]

        # --- dt (distribution transformer) ---
        dt_key = dt_name if dt_code else f"_empty_code_{dt_name}"
        if dt_key not in feeder["dts"]:
            feeder["dts"][dt_key] = {
                "name": dt_name,
                "code": dt_code,
                "meterCount": 0,
                "meterIds": [],
            }
        dt_entry = feeder["dts"][dt_key]
        dt_entry["meterCount"] += 1
        if len(dt_entry["meterIds"]) < 20:  # keep a few samples
            dt_entry["meterIds"].append(meter_id)

    return hierarchy


# Build hierarchy once at startup
_hierarchy_cache = _build_hierarchy(dataset)


@app.get("/api/hierarchy", response_model=dict)
async def get_hierarchy(
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"
    ),
) -> Dict[str, Any]:
    """Reconstructed meter network hierarchy from the exported dataset.

    Returns a nested tree showing zones → circles → divisions → subdivisions
    → substations → feeders → distribution transformers (DTs), with meter
    counts at each level and sample meterIds.

    Query parameters:
    - zone_code: optional filter to a specific zone code

    Response format:
    - zones: dict of zone_name → {code, circles: dict}
    - total_records: total meters in the dataset (403)
    """
    # If a zone_code filter is provided, walk the pre-built tree and
    # return only the matching subtree.
    if zone_code:
        zones = _hierarchy_cache.get("zones", {})
        # Find matching zone
        matching_zone = None
        matching_zone_name = None
        for z_name, z_data in zones.items():
            if z_data.get("code") == zone_code or z_name.replace(" ", "") == zone_code.replace("Z-", ""):
                matching_zone = z_data
                matching_zone_name = z_name
                break
        if matching_zone is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zone with code '{zone_code}' not found",
            )
        return {
            "zones": {matching_zone_name: matching_zone},
            "total_records": _hierarchy_cache["total_records"],
        }

    return {
        "zones": _hierarchy_cache["zones"],
        "total_records": _hierarchy_cache["total_records"],
    }


# ---------------------------------------------------------------------------
# Combined attribute filtering endpoint
# ---------------------------------------------------------------------------

def _attrib_filter(items: List[str],
                   status: Optional[str] = None,
                   make: Optional[str] = None,
                   phase_type: Optional[str] = None,
                   install_type: Optional[str] = None,
                   dt_code: Optional[str] = None,
                   zone_code: Optional[str] = None,
                   circle_code: Optional[str] = None,
                   feeder_code: Optional[str] = None,
                   ) -> List[str]:
    """Apply AND‑combined attribute filters to a list of meterIds.

    Parameters are matched against the in‑memory indexes built at startup.
    Unknown filter values simply narrow results to 0 matches.
    """
    meter_ids: List[str] = list(_by_id.keys())

    if status:
        meter_ids = _by_status.get(status, [])
    elif phase_type:
        meter_ids = _by_phase.get(phase_type, [])
    elif install_type:
        # installType is not indexed; fall through to per-record check below
        pass
    elif dt_code:
        meter_ids = _by_dt.get(dt_code, [])
    elif zone_code:
        meter_ids = _by_zone.get(zone_code, [])
    elif circle_code:
        # circle_code: filter by circle code; some records have empty code
        meter_ids = [_mid for mid in meter_ids
                     if _by_id.get(mid, {}).get("hierarchy", {}).get("circle", {}).get("code", "") == circle_code]
    elif feeder_code:
        meter_ids = [_mid for mid in meter_ids
                     if _by_id.get(mid, {}).get("hierarchy", {}).get("feeder", {}).get("code", "") == feeder_code]

    # Remaining filters that aren't covered by the indexed lookups above:
    # Apply per‑record checks for make, installType, and any remaining dtCode
    # when it wasn't caught by the indexed path.
    filtered: List[str] = []
    for mid in meter_ids:
        rec = _by_id.get(mid)
        if rec is None:
            continue
        # status filter already handled above; skip re-check
        if make and rec.get("make", "") != make:
            continue
        if phase_type and rec.get("phaseType", "") != phase_type:
            continue
        if install_type and rec.get("installType", "") != install_type:
            continue
        # dtCode: check both the explicit dtCode field and the hierarchy dt
        rec_dt = rec.get("dtCode", "")
        rec_h_dt = rec.get("hierarchy", {}).get("dt", {}).get("code", "")
        rec_dt_match = (dt_code is not None and
                        (rec_dt == dt_code or rec_h_dt == dt_code))
        if dt_code and not rec_dt_match:
            continue
        # zone_code from hierarchy
        if zone_code:
            rec_zone = rec.get("hierarchy", {}).get("zone", {}).get("code", "")
            if rec_zone != zone_code:
                continue
        # circle_code from hierarchy
        if circle_code:
            rec_circle = rec.get("hierarchy", {}).get("circle", {}).get("code", "")
            if rec_circle != circle_code:
                continue
        # feeder_code from hierarchy
        if feeder_code:
            rec_feeder = rec.get("hierarchy", {}).get("feeder", {}).get("code", "")
            if rec_feeder != feeder_code:
                continue
        filtered.append(mid)

    return filtered


@app.get("/api/meters/query", response_model=dict)
async def query_meters(
    status: Optional[str] = Query(
        None, regex=r"^(Installed|Faulty|Decommissioned)$",
        description="Filter by installation status"
    ),
    make: Optional[str] = Query(None, description="Filter by meter make"),
    phase_type: Optional[str] = Query(
        None, regex=r"^(single|three)$",
        description="Filter by electrical phase type"
    ),
    install_type: Optional[str] = Query(
        None, description="Filter by installation type"
    ),
    dt_code: Optional[str] = Query(
        None, description="Filter by DT code (DT-001 through DT-040)"
    ),
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (Z-01, Z-02, Z-03)"
    ),
    circle_code: Optional[str] = Query(
        None, description="Filter by circle code (e.g., C-01, or empty)"
    ),
    feeder_code: Optional[str] = Query(
        None, description="Filter by feeder code (e.g., F-001, or empty)"
    ),
    page: int = Query(1, ge=1, description="Page number (1‑indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Dict[str, Any]:
    """List meters with combined attribute filtering (AND semantics).

    Supports filtering by any combination of:
    - ``status`` — installation status
    - ``make`` — meter manufacturer
    - ``phase_type`` — single or three
    - ``install_type`` — CT Operated or Whole Current
    - ``dt_code`` — distribution transformer code
    - ``zone_code`` — zone code from hierarchy
    - ``circle_code`` — circle code from hierarchy
    - ``feeder_code`` — feeder code from hierarchy

    Filters are applied together using AND semantics.  Unknown or
    unmatching filter values simply reduce the result set.

    Pagination follows the same scheme as ``/api/meters``:
    ``page`` and ``per_page`` with ``total_pages`` metadata.

    Empty results return ``{ "meters": [], "total": 0, "page": 1, "total_pages": 0 }``.
    """
    filtered = _attrib_filter(
        list(_by_id.keys()),
        status=status,
        make=make,
        phase_type=phase_type,
        install_type=install_type,
        dt_code=dt_code,
        zone_code=zone_code,
        circle_code=circle_code,
        feeder_code=feeder_code,
    )

    # Pagination
    total = len(filtered)
    page = max(page, 1)
    per_page = max(1, min(per_page, 100))
    total_pages = (total + per_page - 1) // per_page if total else 0
    start = (page - 1) * per_page
    end = start + per_page
    page_items = filtered[start:end]

    # Build summary records
    meters = [_summary_record(_by_id[mid]) for mid in page_items]

    return {
        "meters": meters,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
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


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "message": exc.detail, "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    # In production one would log `exc` securely. Here we return a generic
    # 500 with a minimal message so no secrets leak in the response.
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )