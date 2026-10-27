"""Reorder routes so /api/meters/query comes before /api/meters/{meter_id}."""
with open('app.py') as f:
    content = f.read()

# Find the positions
idx_query = content.find('@app.get("/api/meters/query"')
idx_meter = content.find('@app.get("/api/meters/{meter_id}"')

print(f'query at: {idx_query}')
print(f'meter at: {idx_meter}')

# Extract the query route definition (from @app.get to just before the next @app.get or end of relevant section)
# Find the next @app.get after query
next_query = content.find('@app.get', idx_query + 1)
if next_query < 0:
    next_query = len(content)

query_route = content[idx_query:next_query]

# Find the meter route definition
next_meter = content.find('@app.get', idx_meter + 1)
if next_meter < 0:
    next_meter = len(content)

meter_route = content[idx_meter:next_meter]

print(f'Query route length: {len(query_route)}')
print(f'Meter route length: {len(meter_route)}')

# Swap them: replace the query route section with the meter route, and the meter route section with the query route
# But we need to be careful about the exact boundaries

# New order: query first, then meter
new_content = content[:idx_query] + meter_route + content[idx_query:idx_meter] + query_route + content[idx_meter + len(meter_route):]

# Verify the swap
new_idx_query = new_content.find('@app.get("/api/meters/query"')
new_idx_meter = new_content.find('@app.get("/api/meters/{meter_id}"')
print(f'New query at: {new_idx_query}')
print(f'New meter at: {new_idx_meter}')

# Verify the routes are in the right order
if new_idx_query < new_idx_meter:
    print('SUCCESS: query route now comes before meter route')
else:
    print('FAIL: query route still comes after meter route')

# Write the new content
with open('app.py', 'w') as f:
    f.write(new_content)
print('App.py reordered successfully')