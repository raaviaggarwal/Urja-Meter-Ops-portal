#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find the get_hierarchy function and add debug
# The issue: when zone_code is valid, it returns 500
# Let's look at the logic

# Find "if zone_code:" section
idx = content.find('if zone_code:')
if idx >= 0:
    # Show context around it
    start = max(0, idx - 50)
    end = min(len(content), idx + 200)
    print("=== Zone code filter section ===")
    print(content[start:end])
    
# Also check the matching logic
idx2 = content.find('z_data.get("code")')
if idx2 >= 0:
    start = max(0, idx2 - 100)
    end = min(len(content), idx2 + 200)
    print("=== Zone code matching ===")
    print(content[start:end])
PYEOF