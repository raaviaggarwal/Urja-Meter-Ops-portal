#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import app

# Check the _by_zone dictionary
print('_by_zone keys (first 5):', list(app._by_zone.keys())[:5])
z01 = app._by_zone.get('Z-01', [])
print('_by_zone[\"Z-01\"] (first 3):', z01[:3] if z01 else 'NOT FOUND')

# Check the hierarchy cache
print('_hierarchy_cache zones:', list(app._hierarchy_cache['zones'].keys()))
print('_hierarchy_cache total_records:', app._hierarchy_cache['total_records'])