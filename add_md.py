with open('app.py', 'r') as f:
    lines = f.readlines()

# Insert the metadata function after line 506 (0-indexed), which is after the nearby_meters return
# The nearby_meters function ends at line 506 (1-indexed) / index 505 (0-indexed) with "return {\"meters\": results, \"total\": len(results)}"
# The exception handlers start at line 517 (1-indexed) / index 516 (0-indexed)

new_function = '''@app.get('/api/metadata', response_model=dict)
async def get_metadata() -> Dict[str, Any]:
    \"\"\"Get data source metadata and freshness information.

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

# Insert after line 506 (1-indexed) = after the nearby_meters return
# 0-indexed: insert at position 506 (after the return statement of nearby_meters)
# But the nearby_meters return is at lines[505] (0-indexed)
# Let me insert after lines[505]

# Actually the nearby_meters function is from lines 460 to 506 (1-indexed)
# The return statement is at line 506
# I want to insert after line 506 (1-indexed), which is lines[505] (0-indexed)

# But let me be more precise. Let me find the exact line of the return statement
for i, line in enumerate(lines):
    if 'return {"meters": results, "total": len(results)}' in line:
        return_line = i
        print(f'Return statement at line {i+1} (0-indexed: {i})')
        break

# Insert after the return statement
new_lines = lines[:return_line+1] + [new_function] + lines[return_line+1:]

with open('app.py', 'w') as f:
    f.writelines(new_lines)

print('Metadata endpoint added')
YEEP