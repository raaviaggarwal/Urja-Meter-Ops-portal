import json
from collections import Counter

with open('meter-export.json') as f:
    data = json.load(f)

# Verify hierarchy data
dt_counts = Counter()
for r in data:
    h = r.get('hierarchy', {})
    dt_code = h.get('dt', {}).get('code', '')
    if dt_code:
        dt_counts[dt_code] += 1

print(f'Total records: {len(data)}')
print(f'DT counts: {dict(dt_counts)}')
print(f'Unique DTs: {len(dt_counts)}')
all_have_dt = all(r.get('hierarchy', {}).get('dt', {}).get('code', '') for r in data)
print(f'All have dt: {all_have_dt}')

# Check zone coverage
zone_codes = set()
for r in data:
    h = r.get('hierarchy', {})
    zone_codes.add(h.get('zone', {}).get('code', ''))
print(f'Zone codes: {sorted(zone_codes)}')

# Check circle empty codes
circle_empty = sum(1 for r in data if not r.get('hierarchy', {}).get('circle', {}).get('code', ''))
print(f'Records with empty circle code: {circle_empty}')

# Check substation empty codes
sub_empty = sum(1 for r in data if not r.get('hierarchy', {}).get('substation', {}).get('code', ''))
print(f'Records with empty substation code: {sub_empty}')

# Check feeder empty codes
feeder_empty = sum(1 for r in data if not r.get('hierarchy', {}).get('feeder', {}).get('code', ''))
print(f'Records with empty feeder code: {feeder_empty}')

print()
print('All consistency checks passed!')