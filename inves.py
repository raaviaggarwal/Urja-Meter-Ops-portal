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

# Check /api/meters/query without filters
print('=== /api/meters/query without filters ===')
status, parsed, body = request('GET', '/api/meters/query')
print(f'Status: {status}')
if status == 200:
    print(f'Total: {parsed.get("total")}')
    print(f'Meters: {len(parsed.get("meters", []))}')

# Check /api/meters with no filters
print()
print('=== /api/meters with no filters ===')
status, parsed, body = request('GET', '/api/meters')
print(f'Status: {status}')
if status == 200:
    print(f'Total: {parsed.get("total")}')
    print(f'Meters on page 1: {len(parsed.get("meters", []))}')

# Check individual meter counts per page
print()
print('=== Checking meter count per page ===')
total = 0
for page in [1, 2, 3, 5, 10, 21]:
    status, parsed, body = request('GET', f'/api/meters?page={page}&per_page=20')
    if status == 200:
        n = len(parsed.get('meters', []))
        total += n
        print(f'Page {page}: {n} meters, running total: {total}')

print(f'\\nGrand total across checked pages: {total}')