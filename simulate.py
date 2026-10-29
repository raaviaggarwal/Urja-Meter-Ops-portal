#!/usr/bin/env python3
import sys
sys.path.insert(0, ".")
from app import _hierarchy_cache, _build_hierarchy

zones = _hierarchy_cache.get('zones', {})

# Simulate the get_hierarchy function logic
zone_code = 'Z-01'

matching_zone = None
matching_zone_name = None

for z_name, z_data in zones.items():
    if z_data.get("code") == zone_code or z_name.replace(" ", "") == zone_code.replace("Z-", ""):
        matching_zone = z_data
        matching_zone_name = z_name
        break

print(f"matching_zone: {matching_zone}")
print(f"matching_zone_name: {matching_zone_name}")

if matching_zone is None:
    print("Would raise 404")
else:
    try:
        result = {
            "zones": {matching_zone_name: matching_zone},
            "total_records": _hierarchy_cache["total_records"],
        }
        print(f"Result: {json.dumps(result, indent=2)[:300]}")
    except Exception as e:
        print(f"Error creating result: {type(e).__name__}: {e}")

# Also test without zone_code
print("\n=== Without zone_code ===")
try:
    result2 = {
        "zones": _hierarchy_cache["zones"],
        "total_records": _hierarchy_cache["total_records"],
    }
    print(f"Result2: OK, zones count: {len(result2['zones'])}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")