#!/usr/bin/env python3
with open('app.py', 'rb') as f:
    content = f.read()

# Search for return statements with 'zones' 
# Pattern 1: filtered return
pattern1 = b'"zones": {"matching_zone_name'
# Pattern 2: unfiltered return
pattern2 = b'"zones": _hierarchy_cache'

print("Searching for pattern1...")
idx1 = content.find(pattern1)
if idx1 >= 0:
    print(f"Pattern1 found at byte {idx1}")
    start = max(0, idx1 - 50)
    end = min(len(content), idx1 + 200)
    print(content[start:end])
else:
    print("Pattern1 not found")

print()
print("Searching for pattern2...")
idx2 = content.find(pattern2)
if idx2 >= 0:
    print(f"Pattern2 found at byte {idx2}")
    start = max(0, idx2 - 50)
    end = min(len(content), idx2 + 200)
    print(content[start:end])
else:
    print("Pattern2 not found")