import re

with open('app.py', 'r') as f:
    content = f.read()

# Define the metadata function
metadata_fn = '''\n@app.get("/api/metadata", response_model=dict)
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
    }'''

# Define the nearby_meters function
nearby_fn = '''\n@app.get("/api/meters/nearby", response_model=dict)
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
    return {"meters": results, "total": len(results)}'''

# Insert both functions before the exception handlers
# Find the position: after the last route's return and before @app.exception_handler(HTTPException)

# The exception handler marker
exc_marker = "@app.exception_handler(HTTPException)"
exc_pos = content.find(exc_marker)

if exc_pos >= 0:
    # Insert metadata function first, then nearby function
    new_content = content[:exc_pos] + metadata_fn + nearby_fn + content[exc_pos:]
    with open('app.py', 'w') as f:
        f.write(new_content)
    print("Both endpoints added successfully")
else:
    print("Could not find exception handler marker")