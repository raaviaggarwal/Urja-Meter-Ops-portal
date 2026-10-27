"""Reorder app.py routes so /api/meters/query comes before /api/meters/{meter_id}."""
with open('app.py', 'r') as f:
    content = f.read()

# Find the positions
query_start = content.find('@app.get("/api/meters/query"')
meter_start = content.find('@app.get("/api/meters/{meter_id}"')

print(f'query_start: {query_start}')
print(f'meter_start: {meter_start}')

# Find the end of the query function (next @app.get or end of content)
next_app_get = content.find('\n\n@app.get', query_start)
if next_app_get < 0:
    next_app_get = len(content)

query_block = content[query_start:next_app_get]

# Find the end of the get_meter function
next_app_get2 = content.find('\n\n@app.get', meter_start)
if next_app_get2 < 0:
    next_app_get2 = len(content)

meter_block = content[meter_start:next_app_get2]

print(f'query_block length: {len(query_block)}')
print(f'meter_block length: {len(meter_block)}')

# New order: query first, then meter
new_content = content[:meter_start] + query_block + meter_block + content[next_app_get2:]

# Verify
if new_content.find('@app.get("/api/meters/query"') < new_content.find('@app.get("/api/meters/{meter_id}"'):
    print('SUCCESS: Routes reordered')
else:
    print('FAIL: Routes not reordered')

with open('app.py', 'w') as f:
    f.write(new_content)
print('App.py updated')