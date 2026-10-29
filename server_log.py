#!/usr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000', '--log-level', 'debug'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
import time
time.sleep(3)

# Test the endpoint
try:
    url = 'http://127.0.0.1:8000/api/hierarchy?zone_code=Z-01'
    print(f'Requesting: {url}')
    r = urllib.request.urlopen(url, timeout=5)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'HTTP Error status: {e.code}')
    print(f'Error body: {body}')
    # Print headers
    print(f'Headers: {dict(e.headers)}')
except Exception as e:
    print(f'Other error: {type(e).__name__}: {e}')

proc.terminate()
proc.wait()
print('Done')
PYEOF