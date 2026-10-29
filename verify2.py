#!/usr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

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

# Test the reported problematic endpoints
print('=== /api/meters/query ===')
s, p, b = request('GET', '/api/meters/query')
print(f'Status: {s}')
if s == 200:
    print(f'Total: {p.get("total")}')
    print(f'Meters: {len(p.get("meters", []))}')
else:
    print(f'Error response: {p}')

print()
print('=== /api/hierarchy?zone_code=Z-01 ===')
s, p, b = request('GET', '/api/hierarchy?zone_code=Z-01')
print(f'Status: {s}')
if s == 200:
    print(f'Zones: {list(p.get("zones", {}).keys())}')
    print(f'Total records: {p.get("total_records")}')
else:
    print(f'Error response: {b[:200]}')

print()
print('=== /api/meters (should work) ===')
s, p, b = request('GET', '/api/meters')
print(f'Status: {s}')
if s == 200:
    print(f'Total: {p.get("total")}')
    print(f'Meters on page 1: {len(p.get("meters", []))}')

proc.terminate()
proc.wait()