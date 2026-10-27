"""Reorder routes so /api/meters/query comes before /api/meters/{meter_id}."""
with open('app.py') as f:
    lines = f.readlines()

# Find line numbers for the two route definitions
query_line = None
meter_line = None
for i, line in enumerate(lines):
    if '@app.get("/api/meters/query"' in line:
        query_line = i
    if '@app.get("/api/meters/{meter_id}"' in line:
        meter_line = i

print(f'query_line: {query_line}')
print(f'meter_line: {meter_line}')

if query_line is not None and meter_line is not None and query_line > meter_line:
    # Remove the query route lines and insert them before the meter route
    # The query route spans from query_line to the next @app.get or end
    # Collect all lines from query_line to just before the next @app.get
    new_lines = lines[:query_line]  # remove query from its current position
    
    # Insert the query route before the meter route
    # First, find how many lines the query route occupies
    # Count from query_line to the next @app.get
    insert_pos = meter_line
    new_lines[insert_pos:insert_pos] = lines[query_line:]  # insert query before meter
    
    # Now remove the original query route from its position (but we already did that by not including it in new_lines[:query_line])
    # But we need to also skip the original query route lines when building the rest
    # Actually, let me just rebuild from scratch more carefully
    
    # Let me just take a different approach: build the new file content
    # by iterating through all lines and repositioning
    
print('Alternative approach needed')