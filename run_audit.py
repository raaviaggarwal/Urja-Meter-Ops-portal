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

endpoints = [
    ('GET', '/health'),
    ('GET', '/api/meters'),
    ('GET', '/api/meters/search?query=J100000'),
    ('GET', '/api/meters/status/Installed'),
    ('GET', '/api/meters/J100000'),
    ('GET', '/api/meters/nonexistent'),
    ('GET', '/api/transformers'),
    ('GET', '/api/export/meters'),
    ('GET', '/api/meters/query?status=Installed'),
    ('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5'),
    ('GET', '/api/hierarchy'),
    ('GET', '/api/hierarchy?zone_code=Z-01'),
]

print('=== ENDPOINT TABLE ===')
print('METHOD              PATH                     STATUS SUMMARY')
print('-'*115)

for method, path in endpoints:
    status, parsed, body = request(method, path)
    if status == 200:
        if 'meters' in parsed:
            n = len(parsed.get('meters', []))
            t = parsed.get('total', '?')
            summary = f'total={t}, count={n}'
        elif 'transformers' in parsed:
            t = parsed.get('total', '?')
            summary = f'transformers={t}'
        elif 'count' in parsed:
            c = parsed.get('count', '?')
            summary = f'count={c}'
        else:
            summary = json.dumps(parsed)[:45] if parsed else 'empty'
    elif status == 404:
        summary = 'Not found'
    elif status in (400, 422):
        summary = f'Error {status}'
    else:
        summary = f'Error {status}'
    print(f'{method:15} {path:40} {status:8} {summary}')

proc.terminate()
proc.wait()
print('Server stopped')