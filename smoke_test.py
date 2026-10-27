#!/usr/bin/env python3
"""Phase 9 smoke test: start server and test endpoints."""

import sys
import time
import json
import http.client

sys.path.insert(0, r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal')

# Start uvicorn server
import subprocess
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for server to start
time.sleep(3)

# Check if process is still running
if proc.poll() is not None:
    print("ERROR: Server crashed!")
    print("STDERR:", proc.stderr.read())
    sys.exit(1)

print("Server started successfully")

# Make HTTP requests
conn = http.client.HTTPConnection('127.0.0.1', 8000)

# 1. /health
print("\n=== /health ===")
conn.request('GET', '/health')
resp = conn.getresponse()
body = resp.read().decode()
data = json.loads(body) if body.startswith('{') else body
print(f"Status: {resp.status_code}")
print(f"Body: {body}")

# 2. /api/meters/query?status=Installed
print("\n=== /api/meters/query?status=Installed ===")
conn.request('GET', '/api/meters/query?status=Installed')
resp = conn.getresponse()
body = resp.read().decode()
data = json.loads(body)
print(f"Status: {resp.status_code}")
print(f"Total: {data.get('total')}")
print(f"Meters count: {len(data.get('meters', []))}")

# 3. /api/hierarchy?zone_code=Z-01
print("\n=== /api/hierarchy?zone_code=Z-01 ===")
conn.request('GET', '/api/hierarchy?zone_code=Z-01')
resp = conn.getresponse()
body = resp.read().decode()
data = json.loads(body)
print(f"Status: {resp.status_code}")
print(f"Zones: {list(data.get('zones', {}).keys())}")
total = data.get('total_records', 0)
print(f"Total records: {total}")

# 4. /api/metadata
print("\n=== /api/metadata ===")
conn.request('GET', '/api/metadata')
resp = conn.getresponse()
body = resp.read().decode()
data = json.loads(body)
print(f"Status: {resp.status_code}")
print(f"Record count: {data.get('record_count')}")
print(f"Source file: {data.get('source_file')}")
print(f"Freshness policy: {data.get('freshness', {}).get('policy')}")

# 5. /api/meters/nearby
print("\n=== /api/meters/nearby ===")
conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5')
resp = conn.getresponse()
body = resp.read().decode()
data = json.loads(body)
print(f"Status: {resp.status_code}")
print(f"Total: {data.get('total')}")
print(f"Meters count: {len(data.get('meters', []))}")
if data.get('meters'):
    print(f"Closest: {data['meters'][0]}")

conn.close()

# Kill the server
proc.terminate()
proc.wait()
print("\nServer stopped. Smoke test complete.")