#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add debug print at the start of get_hierarchy function
old_func_start = "async def get_hierarchy(\n    zone_code: Optional[str] = Query(\n        None, description=\"Filter by zone code (e.g., Z-01, Z-02, Z-03)\"\n    ),\n) -> Dict[str, Any]:"

new_func_start = """async def get_hierarchy(
    zone_code: Optional[str] = Query(
        None, description="Filter by zone code (e.g., Z-01, Z-02, Z-03)"
    ),
) -> Dict[str, Any]:
    print(f"DEBUG: get_hierarchy called with zone_code={zone_code!r}", flush=True)
    """ + """    \"\"\"Reconstructed meter network hierarchy from the exported dataset."""

"""

if old_func_start in content:
    content = content.replace(old_func_start, new_func_start)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Modified app.py successfully')
else:
    print('Could not find function start pattern')
    lines = content.split('\n')
    for i in range(805, 815):
        if i < len(lines):
            print(f'{i+1}: {lines[i][:80]}')