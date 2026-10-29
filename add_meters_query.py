#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find the query_meters decorator at line 734 and add /api/meters-query route
# Insert a new @app.get('/api/meters-query') decorator before the existing one

# Actually, let me just insert a new decorator right before line 734
# The new decorator will be: @app.get('/api/meters-query', response_model=dict)

# But wait, the function is async def query_meters, and having two @app.get decorators
# for the same function should work in FastAPI

# Let me insert the new decorator
new_decorator = "@app.get('/api/meters-query', response_model=dict)\n"

# Insert it before line 734 (index 733)
# First check if it's already there
content = ''.join(lines[730:735])
if new_decorator not in content:
    # Insert at line 734 (index 733)
    lines.insert(733, new_decorator)
    with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
        f.writelines(lines)
    print('Added /api/meters-query decorator')
else:
    print('Decorator already exists')