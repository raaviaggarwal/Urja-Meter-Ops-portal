import json
from collections import Counter

with open('meter-export.json') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print()

# Show hierarchy path for first 10 records
print("=== Full hierarchy path for first 10 records ===")
for i in range(10):
    r = data[i]
    h = r.get("hierarchy", {})
    zone = h.get("zone", {}).get("name", "Missing") + " (" + h.get("zone", {}).get("code", "") + ")"
    circle = h.get("circle", {}).get("name", "Missing") + " (" + h.get("circle", {}).get("code", "") + ")"
    division = h.get("division", {}).get("name", "Missing") + " (" + h.get("division", {}).get("code", "") + ")"
    subdivision = h.get("subdivision", {}).get("name", "Missing") + " (" + h.get("subdivision", {}).get("code", "") + ")"
    substation = h.get("substation", {}).get("name", "Missing") + " (" + h.get("substation", {}).get("code", "") + ")"
    feeder = h.get("feeder", {}).get("name", "Missing") + " (" + h.get("feeder", {}).get("code", "") + ")"
    dt = h.get("dt", {}).get("name", "Missing") + " (" + h.get("dt", {}).get("code", "") + ")"
    path = f"Zone={zone}, Circle={circle}, Div={division}, Sub={subdivision}, SS={substation}, Feeder={feeder}, DT={dt}"
    print(f"  {r['meterId']}: {path}")

print()

# Check for records with empty codes at various levels
print("=== Records with empty circle code ===")
for r in data:
    h = r.get("hierarchy", {})
    if not h.get("circle", {}).get("code", ""):
        print(f"  {r['meterId']}: circle code empty, circle name={h.get('circle', {}).get('name', '')}")

print()
print("=== Records with empty substation code ===")
for r in data:
    h = r.get("hierarchy", {})
    if not h.get("substation", {}).get("code", ""):
        print(f"  {r['meterId']}: substation code empty, substation name={h.get('substation', {}).get('name', '')}")

print()
print("=== Records with empty feeder code ===")
for r in data:
    h = r.get("hierarchy", {})
    if not h.get("feeder", {}).get("code", ""):
        print(f"  {r['meterId']}: feeder code empty, feeder name={h.get('feeder', {}).get('name', '')}")

print()
print("=== Meters per DT ===")
dt_counts = Counter()
for r in data:
    h = r.get("hierarchy", {})
    dt_code = h.get("dt", {}).get("code", "")
    if dt_code:
        dt_counts[dt_code] += 1

for dt_code, count in sorted(dt_counts.items()):
    marker = " ***" if count > 10 else ""
    print(f"  {dt_code}: {count}{marker}")

print()
print("=== DTs shared by multiple meters ===")
shared_dts = {dt: count for dt, count in dt_counts.items() if count > 1}
for dt_code, count in sorted(shared_dts.items()):
    print(f"  {dt_code}: {count} meters")