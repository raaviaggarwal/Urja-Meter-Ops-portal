import json
with open('C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal\meter-export.json', 'r') as f:
    data = json.load(f)
print(f'Total meters in export: {len(data)}')
last = data[-1]
print(f'Last meterId: {last["meterId"]}')
print(f'Last serialNo: {last["serialNo"]}')
print(f'Last installStatus: {last["installStatus"]}')
dtcodes = set(m['dtCode'] for m in data)
print(f'Unique dtCodes: {sorted(dtcodes)}')
feedercodes = set()
for m in data:
    for level in m['hierarchy'].values():
        if 'code' in level:
            feedercodes.add(level['code'])
print(f'Unique feeder codes: {sorted(feedercodes)}')
subcodes = set()
for m in data:
    for level in m['hierarchy'].values():
        if 'code' in level:
            subcodes.add(level['code'])
print(f'Unique substation codes: {sorted(subcodes)}')
statuses = set(m['installStatus'] for m in data)
print(f'Status values: {statuses}')
phases = set(m['phaseType'] for m in data)
print(f'Phase types: {phases}')
builds = set(m['build'] for m in data)
print(f'Build types: {builds}')