#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Add a Pydantic model for hierarchy response after the BaseModel import
model_code = '''\n# ---------------------------------------------------------------------------
# Hierarchy response model
# ---------------------------------------------------------------------------

class MeterHierarchyResponse(BaseModel):
    zones: Dict[str, Any]
    total_records: int\n'''

# Find the position after the pydantic import
import_pos = content.find('from pydantic import BaseModel, Field')
if import_pos >= 0:
    # Find the end of that line
    line_end = content.find('\n', import_pos)
    if line_end >= 0:
        # Insert the model after the import line
        new_content = content[:line_end+1] + model_code + content[line_end+1:]
        
        # Now update the get_hierarchy function to use the model
        # Change the return type annotation and returns
        old_returns = '''    # If a zone_code filter is provided, walk the pre-built tree and
    # return only the matching subtree.
    if zone_code:
        zones = _hierarchy_cache.get("zones", {})
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
        return {
            "zones": {matching_zone_name: matching_zone},
            "total_records": _hierarchy_cache["total_records"],
        }

    return {
        "zones": _hierarchy_cache["zones"],
        "total_records": _hierarchy_cache["total_records"],
    }'''

        new_returns = '''    # If a zone_code filter is provided, return hierarchy response
    if zone_code:
        zones = _hierarchy_cache.get("zones", {})
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
        return MeterHierarchyResponse(
            zones={matching_zone_name: matching_zone},
            total_records=_hierarchy_cache["total_records"],
        ).dict()

    return MeterHierarchyResponse(
        zones=_hierarchy_cache["zones"],
        total_records=_hierarchy_cache["total_records"],
    ).dict()'''

    if old_returns in new_content:
        new_content = new_content.replace(old_returns, new_returns)
        
        # Also update the return type annotation
        new_content = new_content.replace(
            '-> Dict[str, Any]:',
            '-> MeterHierarchyResponse:'
        )
        
        with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
            f.write(new_content)
        print("Model added and returns updated successfully")
    else:
        print("Could not find old returns pattern")
        # Let's print what we have
        import re
        match = re.search(r'async def get_hierarchy.*?^}', new_content, re.DOTALL | re.MULTILINE)
        if match:
            print("Found get_hierarchy function")
            print(match.group()[:800])
else:
    print("Could not find import position")