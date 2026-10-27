import json
from collections import Counter

with open('meter-export.json') as f:
    data = json.load(f)

print(f'dataset len: {len(data)}')
print(f'Status counts: {dict(Counter(r["installStatus"] for r in data))}')

dt_codes = set()
for r in data:
    h = r.get('hierarchy', {})
    dt = h.get('dt', {})
    dt_codes.add(dt.get('code', ''))
print(f'Unique DT codes: {len(dt_codes)}')

zone_codes = set()
for r in data:
    h = r.get('hierarchy', {})
    zone = h.get('zone', {})
    zone_codes.add(zone.get('code', ''))
print(f'Zone codes: {sorted(zone_codes)}')

print(f'All counts consistent: {len(data) == 403}')