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

# Test various URL patterns
print('=== Testing route matching ===')
tests = [
    '/api/meters',
    '/api/meters/',
    '/api/meters/query',
    '/api/meters/query?',
    '/api/meters/query?status=Installed',
    '/api/meters/query?make=HPL',
    '/api/meters/search?query=J100000',
]

for path in tests:
    s, p, b = request('GET', path)
    print(f'  {path:30} -> Status: {s}', end='')
    if s == 200:
        print(f', total={p.get("total")}', end='')
        meters = p.get('meters', [])
        print(f', meters={len(meters)}', end='')
    print()

proc.terminate()
proc.wait()
print('Done')