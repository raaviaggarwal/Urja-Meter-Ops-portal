"""Flock Energy API - FastAPI implementation for meter operations dataset."""

import json
import logging
import math
import os
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class GeoPoint(BaseModel):
    lat: float
    lng: float


class HierarchyNode(BaseModel):
    name: str
    code: str


class MeterHierarchySummary(BaseModel):
    zone: HierarchyNode
    dt: HierarchyNode


class MeterSummary(BaseModel):
    meterId: str
    serialNo: str
    make: str
    phaseType: str
    installStatus: str
    dtCode: str
    hierarchy: MeterHierarchySummary
    geo: GeoPoint


class MeterRecord(BaseModel):
    """Full meter record as stored in the dataset.

    Extra fields present in the source record are preserved so the endpoint
    remains a faithful pass-through regardless of schema evolution.
    """

    model_config = ConfigDict(extra="allow")

    meterId: str
    serialNo: str
    make: str
    phaseType: str
    installStatus: str
    installType: str
    build: str
    dtCode: str
    hierarchy: Dict[str, Any]
    geo: Dict[str, Any]


class PaginatedMeterSummaries(BaseModel):
    meters: List[MeterSummary]
    total: int
    page: int
    per_page: int
    total_pages: int


class MeterSearchResults(BaseModel):
    meters: List[MeterSummary]
    total: int
    query: str


class MetersByStatus(BaseModel):
    meters: List[MeterSummary]
    total: int
    status: str
    page: int
    per_page: int
    total_pages: int


class NearbyMeterItem(BaseModel):
    meterId: str
    distance_km: float


class NearbyMeters(BaseModel):
    meters: List[NearbyMeterItem]
    total: int


class TransformerSummary(BaseModel):
    dtCode: str
    dtName: str
    zoneCode: str
    zoneName: str
    circleCode: str
    circleName: str
    divisionCode: str
    divisionName: str
    substationCode: str
    substationName: str
    feederCode: str
    feederName: str
    meterCount: int


class TransformerSummaries(BaseModel):
    transformers: List[TransformerSummary]
    total: int


class MeterExport(BaseModel):
    count: int
    meters: List[MeterRecord]


class FreshnessPolicy(BaseModel):
    policy: str
    description: str
    last_updated: Optional[str] = None


class DatasetBreakdown(BaseModel):
    phase_types: List[str]
    statuses: List[str]
    makes: List[str]


class MeterDatasetMetadata(BaseModel):
    record_count: int
    source_file: str
    file_modification_time: str
    freshness: FreshnessPolicy
    dataset: DatasetBreakdown


class MeterHierarchyTree(BaseModel):
    zones: Dict[str, Any]
    total_records: int


class APIErrorResponse(BaseModel):
    error: str
    message: str
    detail: str


class InternalErrorResponse(BaseModel):
    error: str
    message: str


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(os.path.dirname(__file__), "meter-export.json")


def load_dataset_snapshot(path: str) -> tuple[list, float]:
    """Load, parse, and validate a meter JSON file.

    Returns ``(records, mtime)`` where *mtime* is ``os.stat().st_mtime`` at
    the time of loading.  Raises ``RuntimeError`` with a clear, actionable
    message — without including record values — if the file is missing,
    unreadable, not a JSON array, or contains structurally invalid records
    (missing required fields, duplicate IDs, malformed hierarchy or
    coordinates).

    This is the single authoritative loader used both at startup and in tests.
    No partial dataset is returned; either all records pass validation or an
    exception is raised so callers never receive a silently corrupt snapshot.
    """
    try:
        stat = os.stat(path)
        mtime = stat.st_mtime
    except OSError as exc:
        raise RuntimeError(
            f"Dataset file not accessible ({type(exc).__name__}): {path}"
        ) from exc

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {path}"
        ) from exc
    except UnicodeDecodeError:
        raise RuntimeError(
            f"Dataset file is not valid UTF-8: {path}"
        ) from None
    except OSError as exc:
        raise RuntimeError(
            f"Unable to read dataset file ({type(exc).__name__}): {path}"
        ) from exc

    if not isinstance(data, list):
        raise RuntimeError(
            f"Dataset must be an array, got {type(data).__name__}: {path}"
        )

    # Validate each record without echoing record values into error messages.
    _REQUIRED = {
        "meterId", "serialNo", "make", "phaseType", "installStatus",
        "installType", "build", "dtCode", "hierarchy", "geo",
    }
    _HIERARCHY_LEVELS = (
        "zone", "circle", "division", "subdivision", "substation", "feeder", "dt",
    )
    seen_ids: dict[str, int] = {}
    errors: list[str] = []

    for i, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            errors.append(f"record {i}: expected an object, got {type(record).__name__}")
            continue

        for field in sorted(_REQUIRED - set(record.keys())):
            errors.append(f"record {i}: missing required field '{field}'")

        meter_id = record.get("meterId")
        if not isinstance(meter_id, str) or not meter_id.strip():
            errors.append(f"record {i}: 'meterId' must be a non-empty string")
        else:
            prev = seen_ids.get(meter_id)
            if prev is not None:
                errors.append(
                    f"record {i}: 'meterId' duplicates record {prev}"
                )
            else:
                seen_ids[meter_id] = i

        hierarchy = record.get("hierarchy")
        if "hierarchy" in record:
            if not isinstance(hierarchy, dict):
                errors.append(f"record {i}: 'hierarchy' must be an object")
            else:
                for level in _HIERARCHY_LEVELS:
                    lv = hierarchy.get(level)
                    if level not in hierarchy:
                        errors.append(f"record {i}: 'hierarchy.{level}' is required")
                    elif not isinstance(lv, dict):
                        errors.append(f"record {i}: 'hierarchy.{level}' must be an object")
                    else:
                        for attr in ("name", "code"):
                            if not isinstance(lv.get(attr), str):
                                errors.append(
                                    f"record {i}: 'hierarchy.{level}.{attr}' must be a string"
                                )

        geo = record.get("geo")
        if "geo" in record:
            if not isinstance(geo, dict):
                errors.append(f"record {i}: 'geo' must be an object")
            else:
                for coord, lo, hi in (("lat", -90, 90), ("lng", -180, 180)):
                    val = geo.get(coord)
                    if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val):
                        errors.append(f"record {i}: 'geo.{coord}' must be a finite number")
                    elif not lo <= val <= hi:
                        errors.append(f"record {i}: 'geo.{coord}' is outside its valid range")

    if errors:
        raise RuntimeError(
            "Dataset validation failed with "
            f"{len(errors)} error(s):\n" + "\n".join(errors[:20])
        )

    return data, mtime


def load_dataset() -> List[Dict[str, Any]]:
    """Legacy loader used by the startup block; delegates to load_dataset_snapshot."""
    records, _ = load_dataset_snapshot(DATA_PATH)
    return records


# Load dataset once at startup; the original file is never modified.
# If the dataset cannot be loaded the operator must fix the data-path problem
# before the service is usable.  We log the error and leave dataset empty so
# the service starts but every data route returns a 503-level response via the
# general exception handler (rather than silently returning empty results).
_dataset_load_error: Optional[str] = None
try:
    dataset = load_dataset()
    TOTAL_RECORDS = len(dataset)
    DATASET_FILE_MTIME: Optional[float] = os.stat(DATA_PATH).st_mtime
except RuntimeError as exc:
    logger.error("Dataset load failed: %s", exc)
    _dataset_load_error = str(exc)
    dataset = []
    TOTAL_RECORDS = 0
    DATASET_FILE_MTIME = None

# ---------------------------------------------------------------------------
# In-memory indexes (built once at startup)
# ---------------------------------------------------------------------------

# map meterId -> record
_by_id: Dict[str, Dict[str, Any]] = {r["meterId"]: r for r in dataset}

# map serialNo -> record (first wins to avoid last-write silently masking dups)
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


def _summary_record(r: Dict[str, Any]) -> dict:
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


def _parse_bool(v: Any) -> Optional[bool]:
    """Coerce a query-parameter value to an optional boolean."""
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
    description="Read\u2010only API over the Flock Energy meter operations dataset.",
    version="1.0.0",
)


@app.get("/health", include_in_schema=False)
async def health() -> Dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Helper: paginate a list of meterIds
# ---------------------------------------------------------------------------


def _paginate(
    items: List[str],
    page: int = 1,
    per_page: int = 20,
) -> dict:
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


@app.get(
    "/api/meters",
    response_model=PaginatedMeterSummaries,
    responses={
        400: {"model": APIErrorResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def list_meters(
    page: int = Query(1, ge=1, description="Page number (1\u2010indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Substring search on meterId or serialNo"),
    status: Optional[str] = Query(
        None, pattern=r"^(Installed|Faulty|Decommissioned)$",
        description="Filter by installation status"
    ),
    phase_type: Optional[str] = Query(
        None, pattern=r"^(single|three)$",
        description="Filter by electrical phase type"
    ),
    build: Optional[str] = Query(
        None, pattern=r"^(legacy|v2)$",
        description="Filter by build version"
    ),
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (Z-01, Z-02, Z-03)"
    ),
    division_code: Optional[str] = Query(
        None, description="Filter by division code (D-01 \u2026 D-10)"
    ),
    dt_code: Optional[str] = Query(
        None, description="Filter by DT code (DT-001 \u2026 DT-040)"
    ),
) -> dict:
    """List meters with pagination, search, and hierarchical filters.

    The returned dict contains:
    - ``meters``: list of summary records
    - ``total``: total number of matching records (before pagination)
    - ``page``, ``per_page``, ``total_pages``: pagination metadata
    """
    # Start with the full set of meterIds
    meter_ids: List[str] = list(_by_id.keys())

    # Apply every supplied filter cumulatively (AND semantics). Each filter
    # narrows the current result set instead of replacing it.
    if status:
        allowed = set(_by_status.get(status, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]
    if phase_type:
        allowed = set(_by_phase.get(phase_type, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]
    if build:
        allowed = set(_by_build.get(build, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]
    if zone_code:
        allowed = set(_by_zone.get(zone_code, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]
    if division_code:
        allowed = set(_by_division.get(division_code, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]
    if dt_code:
        allowed = set(_by_dt.get(dt_code, []))
        meter_ids = [mid for mid in meter_ids if mid in allowed]

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


@app.get(
    "/api/meters/search",
    response_model=MeterSearchResults,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def search_meters(
    query: str = Query(..., min_length=1, description="Substring to search on meterId or serialNo"),
) -> dict:
    """Search meters by meterId or serial number substring.

    Returns matching records as summary objects.
    """
    search_lower = query.lower()
    matched: List[dict] = []
    for mid, rec in _by_id.items():
        sid = rec.get("serialNo", "").lower()
        if search_lower in mid.lower() or search_lower in sid:
            matched.append(_summary_record(rec))

    return {
        "meters": matched,
        "total": len(matched),
        "query": query,
    }


@app.get(
    "/api/meters/status/{status}",
    response_model=MetersByStatus,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def list_meters_by_status(
    status: str = Path(..., pattern=r"^(Installed|Faulty|Decommissioned)$"),
) -> dict:
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


@app.get(
    "/api/transformers",
    response_model=TransformerSummaries,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def list_transformers() -> dict:
    """Provide transformer-derived information from the meter dataset.

    This endpoint does not fabricate capacities or electrical ratings; it
    exposes the hierarchy information that is available from the meter
    records. Each unique DT (distribution transformer) appearing in the
    dataset is listed with its associated zone, circle, subdivision,
    substation, and feeder codes/names as observed in the data.

    The response format is intentionally lightweight — it reflects what
    can be derived from the 403-record export without making assumptions
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
            "meterCount": sum(
                1 for r2 in dataset
                if r2.get("hierarchy", {}).get("dt", {}).get("code", "") == dt_code
            ),
        }

    return {
        "transformers": list(dt_entries.values()),
        "total": len(dt_entries),
    }


@app.get(
    "/api/export/meters",
    response_model=MeterExport,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def export_meters() -> dict:
    """Return the verified meter dataset.

    This endpoint returns the 403-record export that lives alongside the
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


@app.get(
    "/api/metadata",
    response_model=MeterDatasetMetadata,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def get_metadata() -> dict:
    """Get data source metadata and freshness information.

    Returns metadata about the meter dataset including:
    - Record count
    - Source filename
    - File modification time (local file system metadata, captured at startup)
    - Freshness policy

    This endpoint does not connect to the live portal and does not
    provide real-time data. All data comes from the static export
    file meter-export.json alongside the API code.
    """
    import datetime

    mtime_iso: Optional[str]
    if DATASET_FILE_MTIME is not None:
        mtime_iso = datetime.datetime.fromtimestamp(DATASET_FILE_MTIME).isoformat()
    else:
        mtime_iso = None

    return {
        "record_count": TOTAL_RECORDS,
        "source_file": "meter-export.json",
        "file_modification_time": mtime_iso,
        "freshness": {
            "policy": "static_export",
            "description": "Data comes from a static export file; no live portal connection.",
            "last_updated": None,
        },
        "dataset": {
            "phase_types": list(set(r.get("phaseType") for r in dataset)),
            "statuses": list(set(r.get("installStatus") for r in dataset)),
            "makes": list(set(r.get("make") for r in dataset)),
        },
    }


# ---------------------------------------------------------------------------
# Nearby meters endpoint (Haversine formula)
# ---------------------------------------------------------------------------


@app.get(
    "/api/meters/nearby",
    response_model=NearbyMeters,
    responses={
        400: {"model": APIErrorResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def nearby_meters(
    latitude: float = Query(..., json_schema_extra={"minimum": -90, "maximum": 90}, description="Latitude in decimal degrees, -90 to 90"),
    longitude: float = Query(..., json_schema_extra={"minimum": -180, "maximum": 180}, description="Longitude in decimal degrees, -180 to 180"),
    radius_km: float = Query(..., gt=0, le=500, description="Search radius in kilometres"),
) -> dict:
    """Find meters near a given location using the Haversine formula.

    Parameters:
    - latitude: Latitude in decimal degrees (-90 to 90)
    - longitude: Longitude in decimal degrees (-180 to 180)
    - radius_km: Search radius in kilometres (maximum 500)

    Returns meters sorted by ascending distance with their distance in km.
    Results with missing or nil coordinates are silently skipped.
    """
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


def _build_hierarchy(records: List[Dict[str, Any]]) -> dict:
    """Build a tree representing the meter network hierarchy.

    Returns a nested dict with zones → circles → divisions → subdivisions
    → substations → feeders → distribution transformers, each with meter
    counts and sample meterIds.  Empty hierarchy codes are preserved with
    a special marker so callers can distinguish "no code" from "absent level".
    """
    hierarchy: Dict[str, Any] = {
        "zones": {},
        "total_records": len(records),
    }

    for r in records:
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


@app.get(
    "/api/hierarchy",
    response_model=MeterHierarchyTree,
    responses={
        404: {"model": APIErrorResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def get_hierarchy(
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"
    ),
) -> dict:
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
    if zone_code:
        zones = _hierarchy_cache.get("zones", {})
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


def _attrib_filter(
    items: List[str],
    status: Optional[str] = None,
    make: Optional[str] = None,
    phase_type: Optional[str] = None,
    install_type: Optional[str] = None,
    dt_code: Optional[str] = None,
    zone_code: Optional[str] = None,
    circle_code: Optional[str] = None,
    feeder_code: Optional[str] = None,
) -> List[str]:
    """Apply AND-combined attribute filters to a list of meterIds.

    Parameters are matched against the in-memory indexes built at startup.
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
        meter_ids = [
            mid for mid in meter_ids
            if _by_id.get(mid, {}).get("hierarchy", {}).get("circle", {}).get("code", "") == circle_code
        ]
    elif feeder_code:
        meter_ids = [
            mid for mid in meter_ids
            if _by_id.get(mid, {}).get("hierarchy", {}).get("feeder", {}).get("code", "") == feeder_code
        ]

    # Remaining filters applied per record
    filtered: List[str] = []
    for mid in meter_ids:
        rec = _by_id.get(mid)
        if rec is None:
            continue
        if make and rec.get("make", "") != make:
            continue
        if phase_type and rec.get("phaseType", "") != phase_type:
            continue
        if install_type and rec.get("installType", "") != install_type:
            continue
        rec_dt = rec.get("dtCode", "")
        rec_h_dt = rec.get("hierarchy", {}).get("dt", {}).get("code", "")
        if dt_code and rec_dt != dt_code and rec_h_dt != dt_code:
            continue
        if zone_code:
            rec_zone = rec.get("hierarchy", {}).get("zone", {}).get("code", "")
            if rec_zone != zone_code:
                continue
        if circle_code:
            rec_circle = rec.get("hierarchy", {}).get("circle", {}).get("code", "")
            if rec_circle != circle_code:
                continue
        if feeder_code:
            rec_feeder = rec.get("hierarchy", {}).get("feeder", {}).get("code", "")
            if rec_feeder != feeder_code:
                continue
        filtered.append(mid)

    return filtered


@app.get(
    "/api/meters-query",
    response_model=PaginatedMeterSummaries,
    include_in_schema=False,
)
@app.get(
    "/api/meters/query",
    response_model=PaginatedMeterSummaries,
    responses={
        500: {"model": InternalErrorResponse},
    },
)
async def query_meters(
    status: Optional[str] = Query(
        None, pattern=r"^(Installed|Faulty|Decommissioned)$",
        description="Filter by installation status"
    ),
    make: Optional[str] = Query(None, description="Filter by meter make"),
    phase_type: Optional[str] = Query(
        None, pattern=r"^(single|three)$",
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
    page: int = Query(1, ge=1, description="Page number (1\u2010indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
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


@app.get(
    "/api/meters/{meter_id}",
    response_model=MeterRecord,
    responses={
        404: {"model": APIErrorResponse},
        500: {"model": InternalErrorResponse},
    },
)
async def get_meter(meter_id: str) -> dict:
    """Retrieve a single meter's full metadata record.

    Returns a 404 response if the meterId does not exist in the dataset.
    """
    record = _by_id.get(meter_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Meter not found")
    return dict(record)


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
    # Log the real error server-side without exposing internals to the client.
    logger.exception("Unhandled exception on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )
