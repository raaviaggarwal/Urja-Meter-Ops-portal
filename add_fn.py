with open('app.py', 'r') as f:
    lines = f.readlines()

# Insert the nearby_meters function before the first exception handler (line 461, 1-indexed)
# That's at 0-indexed position 460
new_function = '''@app.get("/api/meters/nearby", response_model=dict)
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
        h = r.get("hierarchy", {})
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
'''

# Insert at position 459 (after line 459, which is 0-indexed position 458)
# Actually, let me insert at position 459 which is after line 459 (1-indexed)
new_lines = lines[:459] + [new_function] + lines[459:]

with open('app.py', 'w') as f:
    f.writelines(new_lines)

print('Nearby meter endpoint added')