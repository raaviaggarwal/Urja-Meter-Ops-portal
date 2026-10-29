#!/usr/bin/env python3
import sys
sys.path.insert(0, ".")
from app import _hierarchy_cache

zones = _hierarchy_cache.get('zones', {})
zone_code = 'Z-01'

print('Testing zone_code matching:')
print(f'zone_code: {zone_code}')
print()

for z_name, z_data in zones.items():
    code_match = z_data.get('code') == zone_code
    name_match = z_name.replace(' ', '') == zone_code.replace('Z-', '')
    print(f'Zone: {z_name}')
    print(f'  z_data.get("code"): {z_data.get("code")!r}')
    print(f'  code_match: {code_match}')
    print(f'  z_name.replace(" ", ""): {z_name.replace(" ", "")!r}')
    print(f'  zone_code.replace("Z-", ""): {zone_code.replace("Z-", "")!r}')
    print(f'  name_match: {name_match}')
    print()