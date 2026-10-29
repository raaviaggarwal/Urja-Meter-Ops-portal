#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace the zone_code parameter name to just "zone"
# First, find and replace the get_hierarchy function signature and body

# Replace the function parameter
content = content.replace(
    'zone_code: Optional[str] = Query(\n        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"\n    ),',
    'zone_code: Optional[str] = Query(\n        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"\n    ),'
)

# Actually, let me just try a different approach - rename the parameter
# Find the specific line and replace
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'zone_code: Optional[str] = Query(' in line and 'description="Filter by zone code' in line:
        # This is the get_hierarchy parameter
        # Replace the description to test if parameter name matters
        lines[i] = line.replace(
            'description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"',
            'description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"'
        )
        break

content = '\n'.join(lines)

# Now let me also update the function body references from zone_code to the new name
# Actually, let me just test with a completely different parameter name

# Write back
with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)

print("Parameter name test setup done")