#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# First, add the MeterHierarchyResponse model after the pydantic import
# Find "from pydantic import BaseModel, Field"
import_pos = content.find('from pydantic import BaseModel, Field')
if import_pos >= 0:
    # Insert after this line
    model_to_add = '''\n# ---------------------------------------------------------------------------
# Hierarchy response model
# ---------------------------------------------------------------------------

class MeterHierarchyResponse(BaseModel):
    \"\"\"Response model for the /api/hierarchy endpoint.\"\"\"
    zones: Dict[str, Any]
    total_records: int\n'''
    
    # Insert after the import line
    line_end = content.find('\n', import_pos)
    if line_end >= 0:
        new_content = content[:line_end+1] + model_to_add + content[line_end+1:]
        
        # Now update the get_hierarchy function
        # Change response_model to use the new model
        new_content = new_content.replace(
            'response_model=dict',
            'response_model=MeterHierarchyResponse'
        )
        
        # Change the return type annotation
        new_content = new_content.replace(
            '-> Dict[str, Any]:',
            '-> MeterHierarchyResponse:'
        )
        
        # Update the return statements to use the model
        # The returns need to be wrapped in the model
        old_return_pattern = '''        return {\n            "zones": {matching_zone_name: matching_zone},\n            "total_records": _hierarchy_cache["total_records"],\n        }\n\n    return {\n        "zones": _hierarchy_cache["zones"],\n        "total_records": _hierarchy_cache["total_records"],\n    }'''
        
        # Instead of trying to match the exact pattern, let me just wrap the returns
        # Actually, let me take a different approach - just update the response_model and type
        # and see if FastAPI handles it
        
        with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
            f.write(new_content)
        print("Model added and response_model updated successfully")
    else:
        print("Could not find line end after pydantic import")
else:
    print("Could not find pydantic import")