#!/usr/bin/env python3
import subprocess, time, sys, json, urllib.request, urllib.error

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
time.sleep(3)

def request(method, path):
    try:
        url = f'http://127.0.0.1:8000{path}'
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

print('=== ERROR HANDLING TESTS ===')
print()

# 1. Unknown meter ID
print('1. Unknown meter ID:')
status, parsed, body = request('GET', '/api/meters/unknown-meter-id')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 2. Bad query parameter (invalid status filter)
print()
print('2. Bad status filter (not Installed/Faulty/Decommissioned):')
status, parsed, body = request('GET', '/api/meters/status/InvalidStatus')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 3. Bad query parameter on /api/meters/query
print()
print('3. /api/meters/query with bad make parameter:')
status, parsed, body = request('GET', '/api/meters/query?make=InvalidMake')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 4. Bad query parameter on /api/meters (invalid phase_type)
print()
print('4. /api/meters with bad phase_type:')
status, parsed, body = request('GET', '/api/meters?phase_type=invalid')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 5. Nonexistent route
print()
print('5. Nonexistent route:')
status, parsed, body = request('GET', '/api/nonexistent')
print(f'   Status: {status}')
print(f'   Response: {body[:200]}')

# 6. Valid meter ID that exists
print()
print('6. Valid meter J100000:')
status, parsed, body = request('GET', '/api/meters/J100000')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 7. Query with valid filters
print()
print('7. /api/meters/query?status=Faulty:')
status, parsed, body = request('GET', '/api/meters/query?status=Faulty')
print(f'   Status: {status}')
print(f'   Response total: {parsed.get("total")}')

# 8. Query with phase_type=three
print()
print('8. /api/meters/query?phase_type=three:')
status, parsed, body = request('GET', '/api/meters/query?phase_type=three')
print(f'   Status: {status}')
print(f'   Response total: {parsed.get("total")}')

# 9. nearby with invalid lat
print()
print('9. /api/meters/nearby with invalid latitude:')
status, parsed, body = request('GET', '/api/meters/nearby?latitude=200&longitude=75.830957&radius_km=5')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

# 10. hierarchy with invalid zone
print()
print('10. /api/hierarchy?zone_code=Z-999 (invalid zone):')
status, parsed, body = request('GET', '/api/hierarchy?zone_code=Z-999')
print(f'   Status: {status}')
print(f'   Response: {json.dumps(parsed)[:200]}')

proc.terminate()
proc.wait()
print()
print('Server stopped')