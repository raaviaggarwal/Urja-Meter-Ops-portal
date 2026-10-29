#!/usr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Get the full error response
try:
    url = 'http://127.0.0.1:8000/api/meters/query'
    r = urllib.request.urlopen(url, timeout=5)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'HTTP Error status: {e.code}')
    print(f'Error body: {body}')
    parsed = json.loads(body) if body else {}
    print(f'Parsed: {parsed}')
except Exception as e:
    print(f'Other error: {e}')

proc.terminate()
proc.wait()