"""Clean up duplicate routes in app.py."""
with open('app.py', 'r') as f:
    content = f.read()

# Remove duplicate /api/meters/{meter_id} at line 658 (keep the one at 319)
# Find and remove the second occurrence
# The second {meter_id} is at position 658, we need to remove it and everything up to the next unique route

# Find all @app.get positions
import re
positions = [m.start() for m in re.finditer(r'@app\.get\(", app.py)]

# Print all @app.get positions with line numbers
for i, pos in enumerate(positions):
    # Find line number
    line_num = content.count('\n', 0, pos) + 1
    # Get the line
    line_end = content.find('\n', pos)
    line = content[pos:line_num].split('\n')[-1] if line_end > pos else content[pos:]
    print(f'Line {line_num}: {line.strip()[:80]}')
" 2>&1