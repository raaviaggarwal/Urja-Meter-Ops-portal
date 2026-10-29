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

# Test if /api/meters/query gets intercepted by list_meters
print('=== Debugging route matching ===')
s, p, b = request('GET', '/api/meters')
print(f'/api/meters (no params): status={s}, total={p.get("total")}')

s, p, b = request('GET', '/api/meters?status=Installed')
print(f'/api/meters?status=Installed: status={s}, total={p.get("total")}')

s, p, b = request('GET', '/api/meters/query')
print(f'/api/meters/query: status={s}')

s, p, b = request('GET', '/api/meters/query/')
print(f'/api/meters/query/: status={s}')

proc.terminate()
proc.wait()
print('Done')