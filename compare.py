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

# Test list_meters vs query_meters
print('=== Testing list_meters vs query_meters ===')
tests = [
    '/api/meters?status=Installed',
    '/api/meters?make=HPL',
    '/api/meters/query?status=Installed',
    '/api/meters/query?make=HPL',
    '/api/meters?search=J100000',
    '/api/meters/search?query=J100000',
]

for path in tests:
    s, p, b = request('GET', path)
    total = p.get('total', 'N/A')
    meter_count = len(p.get('meters', []))
    print(f'  {path:35} -> Status: {s}, total={total}, meters={meter_count}')

proc.terminate()
proc.wait()
print('Done')