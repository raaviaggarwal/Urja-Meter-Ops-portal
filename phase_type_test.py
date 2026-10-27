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

# Test phase_type=three multiple times
for i in range(3):
    print(f'Attempt {i+1}: /api/meters/query?phase_type=three')
    status, parsed, body = request('GET', '/api/meters/query?phase_type=three')
    print(f'  Status: {status}')
    if status == 500:
        print(f'  Error body: {body[:500]}')
    elif status == 200:
        total = parsed.get("total", "?")
        print(f'  Total: {total}')
    print()

# Also test status=Faulty
print('---')
print('status=Faulty:')
status, parsed, body = request('GET', '/api/meters/query?status=Faulty')
print(f'  Status: {status}')
if status == 200:
    total = parsed.get("total", "?")
    print(f'  Total: {total}')

# Test status=Decommissioned
print('---')
print('status=Decommissioned:')
status, parsed, body = request('GET', '/api/meters/query?status=Decommissioned')
print(f'  Status: {status}')
if status == 200:
    total = parsed.get("total", "?")
    print(f'  Total: {total}')