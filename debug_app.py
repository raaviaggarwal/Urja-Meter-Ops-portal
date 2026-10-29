#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_hierarchy function and add a debug print just before the return
old_return = """    return {
            "zones": {matching_zone_name: matching_zone},
            "total_records": _hierarchy_cache["total_records"],
        }"""

new_return = """    import sys as _sys
    _dbg = _sys.stdout.write
    _dbg(f"DEBUG: matching_zone_name={matching_zone_name!r}, type={type(matching_zone_name)}")
    _dbg(f"DEBUG: matching_zone keys={list(matching_zone.keys()) if matching_zone else None}")
    _dbg(f"DEBUG: _hierarchy_cache keys={list(_hierarchy_cache.keys())}")
    _dbg(f"DEBUG: about to return")
    return {
        "zones": {matching_zone_name: matching_zone},
        "total_records": _hierarchy_cache["total_records"],
    }"""

if old_return in content:
    content = content.replace(old_return, new_return)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Modified app.py successfully')
else:
    print('Could not find the return statement pattern')
    # Show what we're looking for
    idx = content.find('return {')
    if idx >= 0:
        print(f'Found "return {{" at position {idx}')
        print(content[idx:idx+200])