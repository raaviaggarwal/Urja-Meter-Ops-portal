#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Add a Pydantic model for hierarchy response and update the endpoint
# First, add the model before the app FastAPI initialization or after the BaseModel import

# Let me find a good place to add the model - after the import section
model_insertion = '''# ---------------------------------------------------------------------------
# Hierarchy response model
# ---------------------------------------------------------------------------

class MeterHierarchyResponse(BaseModel):
    zones: Dict[str, Any]
    total_records: int


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------'''

# Find the position after the import section (after line 55 or so)
# Actually, let me find "Data loading" section end
import_regex = r'# Load dataset once at startup'
pos = content.find(import_regex)
if pos >= 0:
    # Find the end of the dataset loading section
    end_pos = content.find('\n#', pos + 1)
    if end_pos >= 0:
        # Insert the model before the FastAPI app creation
        model_section = '''\n# ---------------------------------------------------------------------------
# Hierarchy response model
# ---------------------------------------------------------------------------

class MeterHierarchyResponse(BaseModel):
    zones: Dict[str, Any]
    total_records: int



'''}
        new_content = content[:end_pos] + model_section + content[end_pos:]
        
        # Also update the get_hierarchy return to use the model
        # Change the return statements to return MeterHierarchyResponse objects
        old_return1 = '''        return {\n            "zones": {matching_zone_name: matching_zone},\n            "total_records": _hierarchy_cache["total_records"],\n        }\n\n    return {\n        "zones": _hierarchy_cache["zones"],\n        "total_records": _hierarchy_cache["total_records"],\n    }'''
        
        new_return = '''        return MeterHierarchyResponse(
            zones={matching_zone_name: matching_zone},
            total_records=_hierarchy_cache["total_records"],
        ).dict()\n\n    return MeterHierarchyResponse(
        zones=_hierarchy_cache["zones"],
        total_records=_hierarchy_cache["total_records"],
    ).dict()'''
        
        if old_return1 in new_content:
            new_content = new_content.replace(old_return1, new_return)
            with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
                f.write(new_content)
            print("Model added and returns updated")
        else:
            print("Could not find old return pattern")
    else:
        print("Could not find section end")
else:
    print("Could not find import section")