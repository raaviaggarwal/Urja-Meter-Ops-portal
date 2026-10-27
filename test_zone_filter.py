"""Test the hierarchy zone_code filter."""
from app import _hierarchy_cache

# Test the zone filter logic
zones = _hierarchy_cache.get('zones', {})
print('Zones:', list(zones.keys()))
for z_name, z_data in zones.items():
    print(f'  {z_name}: code={z_data.get("code")}')

# Test looking for Z-01
target_code = 'Z-01'
matching = None
for z_name, z_data in zones.items():
    if z_data.get('code') == target_code:
        matching = z_data
        print(f'Found match: {z_name}')
        break
if matching is None:
    print(f'No zone found with code {target_code}')