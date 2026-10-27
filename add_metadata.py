with open('app.py', 'r') as f:
    lines = f.readlines()

# Find the position to insert: after line 459 (0-indexed: 458 is the closing of query_meters)
# Let me find the exact line numbers
for i, line in enumerate(lines):
    if 'total_pages":' in line and i > 450 and i < 470:
        print(f'Line {i+1}: {line.rstrip()}')

# Insert the metadata function after line 459 (0-indexed: after line index 458)
# The query_meters function ends around line 459

new_function = '''@app.get('/api/metadata', response_model=dict)
async def get_metadata() -> Dict[str, Any]:
    '''Get data source metadata and freshness information.

    Returns metadata about the meter dataset including:
    - Record count
    - Source filename
    - File modification time (local file system metadata)
    - Freshness policy

    This endpoint does not connect to the live portal and does not
    provide real-time data. All data comes from the static export
    file meter-export.json alongside the API code.
    '''
'''

# Insert after line 459 (1-indexed) which is index 458 (0-indexed)
# Actually the query_meters function seems to end around line 458-460
# Let me insert after the blank line following query_meters

new_lines = lines[:460] + [new_function] + lines[460:]

with open('app.py', 'w') as f:
    f.writelines(new_lines)

print('Metadata endpoint added')
" 2>&1 | head -20