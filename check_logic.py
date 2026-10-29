#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import app

# Manually call the get_hierarchy logic with zone_code='Z-01'
zone_code = 'Z-01'

zones = app._hierarchy_cache.get('zones', {})
print('zones:', list(zones.keys()))

matching_zone = None
matching_zone_name = None
for z_name, z_data in zones.items():
    code = z_data.get('code')
    code_match = code == zone_code
    print(f'Checking zone: {z_name}, code: {code}, code_match: {code_match}')
    name_match = z_name.replace(' ', '') == zone_code.replace('Z-', '')
    if code_match or name_match:
        matching_zone = z_data
        matching_zone_name = z_name
        print(f'  -> MATCH!')
        break

print(f'matching_zone_name: {matching_zone_name}')
print(f'matching_zone type: {type(matching_zone)}')

if matching_zone is None:
    print('Would raise 404')
else:
    try:
        result = {
            'zones': {matching_zone_name: matching_zone},
            'total_records': app._hierarchy_cache['total_records'],
        }
        print(f'Result: OK, zones keys: {list(result["zones"].keys())}')
    except Exception as e:
        print(f'Error creating result: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()