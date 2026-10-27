#!/usr/bin/env python3
"""Phase 9 smoke test: start server and test endpoints on port 8001."""

import subprocess, time, json, sys, http.client

sys.path.insert(0, r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal')

# Start uvicorn server on port 8002
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8002'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(3)

if proc.poll() is not None:
    print('Server crashed!')
    print('STDERR:', proc.stderr.read())
    sys.exit(1)

print('Server started on port 8002')

conn = http.client.HTTPConnection('127.0.0.1', 8002)

# 1. /health
conn.request('GET', '/health')
resp = conn.getresponse()
body = resp.read().decode()
print(f'/health: Status {resp.status}')
print(f'  Body: {body[:100]}')

# 2. /api/meters/query?status=Installed
conn.request('GET', '/api/meters/query?status=Installed')
resp = conn.getresponse()
data = json.loads(resp.read().decode())
print(f'/api/meters/query?status=Installed: Status {resp.status}')
print(f'  Total: {data.get("total")}')
print(f'  Meters count: {len(data.get("meters", []))}')

# 3. /api/hierarchy?zone_code=Z-01
conn.request('GET', '/api/hierarchy?zone_code=Z-01')
resp = conn.getresponse()
data = json.loads(resp.read().decode())
print(f'/api/hierarchy?zone_code=Z-01: Status {resp.status}')
print(f'  Zones: {list(data.get("zones", {}).keys())}')
print(f'  Total records: {data.get("total_records")}')

# 4. /api/metadata
conn.request('GET', '/api/metadata')
resp = conn.getresponse()
data = json.loads(resp.read().decode())
print(f'/api/metadata: Status {resp.status}')
print(f'  Record count: {data.get("record_count")}')
print(f'  Source file: {data.get("source_file")}')
print(f'  Freshness policy: {data.get("freshness", {}).get("policy")}')

# 5. /api/meters/nearby
conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5')
resp = conn.getresponse()
data = json.loads(resp.read().decode())
print(f'/api/meters/nearby: Status {resp.status}')
print(f'  Total: {data.get("total")}')
print(f'  Meters count: {len(data.get("meters", []))}')
if data.get('meters'):
    print(f'  Closest: {data["meters"][0]}')

conn.close()
proc.terminate()
proc.wait()
print('Smoke test complete.')