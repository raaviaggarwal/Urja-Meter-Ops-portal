#!/usr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Test various endpoints
tests = [
    '/api/meters/query',
    '/api/meters-query',
    '/api/meters',
]

for path in tests:
    try:
        url = 'http://127.0.0.1:8000' + path
        print(f'Requesting: {path}')
        r = urllib.request.urlopen(url, timeout=5)
        body = r.read().decode()
        parsed = json.loads(body) if body else {}
        print(f'  Status: {r.status}')
        total = parsed.get('total', 'N/A')
        print(f'  total: {total}')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'  Status: {e.code}, Body: {body[:100]}')
    except Exception as e:
        print(f'  Error: {type(e).__name__}: {e}')
    print()

proc.terminate()
proc.wait()
print('Done')