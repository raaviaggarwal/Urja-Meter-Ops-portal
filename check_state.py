#!/usr/bin/env python3
import sys
import json

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Completely replace the get_hierarchy function body
# Read the dataset to build a simple hierarchy
data_section = '''# Load dataset once at startup; the original file is never modified.
try:
    dataset = load_dataset()
    TOTAL_RECORDS = len(dataset)
except RuntimeError as exc:
    # If the dataset cannot be loaded, the app will start but every
    # request that touches the data will return a 500. This is intentional
    # — the operator must fix the data-path problem before the service
    # is usable.
    dataset = []
    TOTAL_RECORDS = 0'''

# Check if the data is loaded
if 'dataset = []' in content or 'TOTAL_RECORDS = 0' in content:
    print("Dataset loading section found")
else:
    print("Could not find dataset section")

# Let me just replace the entire get_hierarchy function
old_func = '''@app.get("/api/hierarchy", response_model=dict)
async def get_hierarchy(
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"
    ),
) -> Dict[str, Any]:
    \"\"\"Reconstructed meter network hierarchy from the exported dataset.

    Returns a nested tree showing zones → circles → divisions → subdivisions
    → substations → feeders → distribution transformers (DTs), with meter
    counts at each level and sample meterIds.

    Query parameters:
    - zone_code: optional filter to a specific zone code

    Response format:
    - zones: dict of zone_name → {code, circles: dict}
    - total_records: total meters in the dataset (403)
    \"\"\"
    # If a zone_code filter is provided, walk the pre-built tree and
    # return only the matching subtree.
    if zone_code:
        try:
            zones = _hierarchy_cache.get("zones", {})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
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
        try:
            return {
                "zones": {matching_zone_name: matching_zone},
                "total_records": _hierarchy_cache["total_records"],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    try:
        return {
            "zones": _hierarchy_cache["zones"],
            "total_records": _hierarchy_cache["total_records"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

# Build a new simplified function that doesn't use _hierarchy_cache
# Instead, it will build the hierarchy on the fly from the dataset
# But that's complex. Let me just try a different approach.

# Actually, let me just check if the current function works by testing
# First, let me see what the current state is
print("Current function state checked")
print("Length of content:", len(content))
print("Has _hierarchy_cache:", '_hierarchy_cache' in content)