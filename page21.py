#!/usr/bin/env python3
import urllib.request, json

def request(method, path):
    try:
        url = 'http://127.0.0.1:8000' + path
        r = urllib.request.urlopen(url, timeout=10)
        body = r.read().decode()
        parsed = json.loads(body) if body else {}
        return r.status, parsed, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        parsed = json.loads(body) if body else {}
        return e.code, parsed, body
    except Exception as e:
        return None, str(e), str(e)

# Check page 21 specifically
print('=== Page 21 check ===')
for page_num in [20, 21, 22]:
    status, parsed, body = request('GET', f'/api/meters?page={page_num}&per_page=20')
    if status == 200:
        meters = parsed.get('meters', [])
        print(f'Page {page_num}: {len(meters)} meters')
        for m in meters:
            print(f'  {m.get("meterId")}')
    else:
        print(f'Page {page_num}: status={status}')

# Now check total unique meterIds across all pages
print()
print('=== Check for duplicate meterIds across pages ===')
all_mids = []
for page_num in range(1, 22):
    status, parsed, body = request('GET', f'/api/meters?page={page_num}&per_page=20')
    if status == 200:
        meters = parsed.get('meters', [])
        for m in meters:
            all_mids.append(m.get('meterId'))

print(f'Total meterId entries: {len(all_mids)}')
unique_mids = set(all_mids)
print(f'Unique meterIds: {len(unique_mids)}')
print(f'Duplicates: {len(all_mids) - len(unique_mids)}')