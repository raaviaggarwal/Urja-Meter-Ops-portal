#!/usr/bin/env python3
import json, sys
sys.path.insert(0, ".")
from app import _hierarchy_cache, dataset

zones = _hierarchy_cache.get("zones", {})
print("Number of zones:", len(zones))
print("Zone names:", list(zones.keys())[:10])

# Show first zone structure
first_name = list(zones.keys())[0]
first_zone = zones[first_name]
print("First zone name:", first_name)
print("First zone data keys:", list(first_zone.keys()))
print("First zone code:", first_zone.get("code"))
print("First zone circles keys:", list(first_zone.get("circles", {}).keys())[:5])

# Now check what zone codes exist in the dataset
zone_codes = set()
for r in dataset:
    zc = r.get('zoneCode', '')
    if zc:
        zone_codes.add(zc)
print("\nUnique zone codes in dataset:", sorted(zone_codes)[:20])