import os
import json
import datetime

# Check meter-export.json
path = 'meter-export.json'
print(f'meter-export.json exists: {os.path.isfile(path)}')
print(f'File size: {os.path.getsize(path)} bytes')

# Check modification time
stat = os.stat(path)
mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
print(f'Modification time: {stat.st_mtime}')
print(f'Modification time (human): {mtime}')

# Load and check content
with open(path) as f:
    data = json.load(f)
print(f'Record count: {len(data)}')

# Check for any timestamp field
has_timestamp = False
for r in data[:5]:
    for key in ['lastUpdated', 'timestamp', 'updatedAt']:
        if key in r:
            has_timestamp = True
            print(f'Found {key} field in record: {r[key]}')

if not has_timestamp:
    print('No timestamp field found in records')

# Data analysis
phase_types = set(r.get('phaseType') for r in data)
print(f'Phase types: {phase_types}')

statuses = set(r.get('installStatus') for r in data)
print(f'Statuses: {statuses}')

makes = set(r.get('make') for r in data)
print(f'Makes: {makes}')