#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace zone_code parameter with zone in the get_hierarchy function
# Replace the function parameter
content = content.replace(
    'zone_code: Optional[str] = Query(\n        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"\n    ),',
    'zone: Optional[str] = Query(\n        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"\n    ),'
)

# Now replace the references to zone_code inside the function body
# But careful - we need to only replace the parameter, not the internal variable
# Let me just replace the parameter and see what happens

# Write back
with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)

print("Parameter renamed to 'zone'")