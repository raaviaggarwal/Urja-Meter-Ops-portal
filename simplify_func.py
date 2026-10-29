#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Simplify the get_hierarchy function to return a flat dict
old_func = '''@app.get("/api/hierarchy", response_model=dict)
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
    }'''

new_func = '''@app.get("/api/hierarchy", response_model=dict)
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
        # Return a simplified response
        return {
            "zones": {matching_zone_name: {"code": matching_zone.get("code", ""), "circles": {}}},
            "total_records": _hierarchy_cache["total_records"],
        }

    return {
        "zones": _hierarchy_cache["zones"],
        "total_records": _hierarchy_cache["total_records"],
    }'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
    print("Function simplified successfully")
else:
    print("Could not find old function pattern")