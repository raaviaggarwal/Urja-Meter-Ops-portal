import json
from collections import Counter

with open('meter-export.json') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print()

# Check hierarchy completeness
print("=== Hierarchy level completeness ===")
level_counts = {}
for r in data:
    h = r.get("hierarchy", {})
    for level in ["zone", "circle", "division", "subdivision", "substation", "feeder", "dt"]:
        if level not in h:
            level_counts.setdefault(level, 0)
            level_counts[level] += 1
        else:
            code = h[level].get("code", "")
            if not code:
                level_counts.setdefault(level + "_empty_code", 0)
                level_counts[level + "_empty_code"] += 1

for level in ["zone", "circle", "division", "subdivision", "substation", "feeder", "dt"]:
    total = level_counts.get(level, 0) + level_counts.get(level + "_empty_code", 0)
    empty = level_counts.get(level + "_empty_code", 0)
    missing = level_counts.get(level, 0)
    print(f"  {level}: {total} have it, {empty} have empty code, {missing} missing entirely")

print()

# Check for empty codes
print("=== Empty codes by level ===")
for level in ["zone", "circle", "division", "subdivision", "substation", "feeder", "dt"]:
    empty_records = []
    for i, r in enumerate(data):
        h = r.get("hierarchy", {})
        if level in h and not h[level].get("code", ""):
            empty_records.append(r["meterId"])
    if empty_records:
        print(f"  {level}: {len(empty_records)} records with empty code")
        print(f"    First 5: {empty_records[:5]}")
    else:
        print(f"  {level}: no empty codes")

print()

# Check zone codes distribution
print("=== Zone codes distribution ===")
zone_codes = Counter(r["hierarchy"]["zone"]["code"] for r in data if "zone" in r["hierarchy"] and "zone" in r["hierarchy"]["zone"])
for code, count in sorted(zone_codes.items()):
    print(f"  {code}: {count}")

print()
print("=== Circle codes distribution ===")
circle_codes = Counter(r["hierarchy"]["circle"]["code"] for r in data if "circle" in r["hierarchy"] and "circle" in r["hierarchy"]["circle"])
for code, count in sorted(circle_codes.items()):
    print(f"  {code}: {count}")

print()
print("=== DT codes distribution ===")
dt_codes = Counter(r["hierarchy"]["dt"]["code"] for r in data if "dt" in r["hierarchy"] and "dt" in r["hierarchy"]["dt"])
for code, count in sorted(dt_codes.items()):
    print(f"  {code}: {count}")

print()
print("=== Check for orphaned records (DT not in any other meter's hierarchy DT) ===")
all_dt_codes = set()
for r in data:
    h = r.get("hierarchy", {})
    dt_code = h.get("dt", {}).get("code", "")
    if dt_code:
        all_dt_codes.add(dt_code)

print(f"  Unique DT codes across all meters: {len(all_dt_codes)}")
print(f"  DT codes: {sorted(all_dt_codes)[:10]}...{sorted(all_dt_codes)[-5:]}")

print()
print("=== Meters per DT ===")
dt_meter_count = Counter()
for r in data:
    h = r.get("hierarchy", {})
    dt_code = h.get("dt", {}).get("code", "")
    if dt_code:
        dt_meter_count[dt_code] += 1

for dt_code, count in sorted(dt_meter_count.items()):
    print(f"  {dt_code}: {count} meters")

print()
print("=== Check for same DT shared by meters ===")
# Find DTs shared by multiple meters
shared_dts = {dt: count for dt, count in dt_meter_count.items() if count > 1}
print(f"  DTs shared by >1 meter: {len(shared_dts)}")
for dt_code, count in sorted(shared_dts.items())[:5]:
    print(f"    {dt_code}: {count} meters")

print()
print("=== Full hierarchy path for first 10 records ===")
for i in range(10):
    r = data[i]
    h = r.get("hierarchy", {})
    path = " → ".join([f"{level}: {h.get(level, {}).get('name', '')} ({h.get(level, {}).get('code', '')})" for level in ["zone", "circle", "division", "subdivision", "substation", "feeder", "dt"]])
    print(f"  {r['meterId']}: {path}")