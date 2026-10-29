#!/usr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Get the routes from FastAPI
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/openapi.json', timeout=5)
    data = json.loads(r.read().decode())
    paths = list(data.get('paths', {}).keys())
    print('Registered routes:')
    for p in sorted(paths):
        print(f'  {p}')
except Exception as e:
    print(f'Error: {e}')

proc.terminate()
proc.wait()
print('Done')