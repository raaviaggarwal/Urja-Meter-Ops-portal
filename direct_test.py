#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app import _hierarchy_cache, MeterHierarchyTree
from fastapi import Query

# Simulate what FastAPI would do
# Call the function logic manually

async def test_function(zone_code='Z-01'):
    zones = _hierarchy_cache.get('zones', {})
    matching_zone = None
    matching_zone_name = None
    for z_name, z_data in zones.items():
        if z_data.get('code') == zone_code or z_name.replace(' ', '') == zone_code.replace('Z-', ''):
            matching_zone = z_data
            matching_zone_name = z_name
            break
    if matching_zone is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f'Zone with code "{zone_code}" not found')
    result = {
        'zones': {matching_zone_name: matching_zone},
        'total_records': _hierarchy_cache['total_records'],
    }
    return result

try:
    result = asyncio.run(test_function('Z-01'))
    print('Function result OK')
    print('Result keys:', result.keys())
    # Try Pydantic validation
    validated = MeterHierarchyTree(**result)
    print('Pydantic validation OK')
    print('Validated:', validated)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()