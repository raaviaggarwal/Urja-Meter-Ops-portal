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

print('=== PAGINATION CHECK: list all pages of /api/meters ===')
status, parsed, body = request('GET', '/api/meters?page=1&per_page=20')
print(f'Page 1: status={status}, total={parsed.get("total")}, count={len(parsed.get("meters", []))}')

total = parsed.get('total', 0)
per_page = 20
total_pages = (total + per_page - 1) // per_page if total else 0
print(f'Expected total pages: {total_pages} (total={total}, per_page={per_page})')

# Check last page
last_page = min(total_pages, 21)
status, parsed, body = request('GET', f'/api/meters?page={last_page}&per_page=20')
print(f'Page {last_page}: status={status}, total={parsed.get("total")}, count={len(parsed.get("meters", []))}')

# Check all pages
all_meters = list(parsed.get('meters', []))
for page in range(2, last_page + 1):
    status, parsed, body = request('GET', f'/api/meters?page={page}&per_page=20')
    meters = parsed.get('meters', [])
    all_meters.extend(meters)
    print(f'Page {page}: status={status}, got {len(meters)} meters')

print(f'\\nTotal meters collected across all pages: {len(all_meters)}')
print(f' API-reported total: {total}')
print(f' Match: {len(all_meters) == total}')

# Also check query endpoint pagination
print()
print('=== PAGINATION CHECK: /api/meters/query with status=Installed ===')
status, parsed, body = request('GET', '/api/meters/query?status=Installed&page=1&per_page=5')
print(f'Page 1: status={status}, total={parsed.get("total")}, count={len(parsed.get("meters", []))}')

total_q = parsed.get('total', 0)
per_page_q = 5
total_pages_q = (total_q + per_page_q - 1) // per_page_q if total_q else 0
print(f'Expected total pages: {total_pages_q} (total={total_q}, per_page={per_page_q})')

all_meters_q = list(parsed.get('meters', []))
for page in range(2, total_pages_q + 1):
    status, parsed, body = request('GET', f'/api/meters/query?status=Installed&page={page}&per_page=5')
    meters = parsed.get('meters', [])
    all_meters_q.extend(meters)
    print(f'Page {page}: got {len(meters)} meters')

print(f'Total meters collected: {len(all_meters_q)}')
print(f'API-reported total: {total_q}')
print(f' Match: {len(all_meters_q) == total_q}')

# Check zone_code=Z-01 bug
print()
print('=== ZONE_CODE Z-01 bug check ===')
status, parsed, body = request('GET', '/api/hierarchy?zone_code=Z-01')
print(f'/api/hierarchy?zone_code=Z-01: status={status}')
if status == 500:
    print(f'  ERROR: {body[:200]}')
elif status == 200:
    print(f'  Zones: {list(parsed.get("zones", {}).keys())}')
    print(f'  total_records: {parsed.get("total_records")}')