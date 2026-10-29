#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app import app, _hierarchy_cache, get_hierarchy, MeterHierarchyTree
from fastapi import Query

# Test the core logic
zones = _hierarchy_cache.get('zones', {})
zone_code = 'Z-01'

matching_zone = None
matching_zone_name = None
for z_name, z_data in zones.items():
    if z_data.get('code') == zone_code or z_name.replace(' ', '') == zone_code.replace('Z-', ''):
        matching_zone = z_data
        matching_zone_name = z_name
        break

print(f'matching_zone_name: {matching_zone_name}')
print(f'matching_zone type: {type(matching_zone)}')
print(f'matching_zone has code: {matching_zone.get("code") if matching_zone else None}')

# Now try to build the return value
result = {
    'zones': {matching_zone_name: matching_zone},
    'total_records': _hierarchy_cache['total_records'],
}
print(f'result zones keys: {list(result["zones"].keys())}')
print(f'total_records: {result["total_records"]}')

# Try Pydantic validation
try:
    validated = MeterHierarchyTree(**result)
    print(f'Validated OK: {validated}')
except Exception as e:
    print(f'Validation error: {type(e).__name__}: {e}')