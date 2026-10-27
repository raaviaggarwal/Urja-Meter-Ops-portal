#!/usr/bin/env python3
"""Phase 9 smoke test: start server and test endpoints on fresh port."""

import subprocess, time, json, sys, http.client, os

sys.path.insert(0, r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal')

# Kill any existing python processes on ports 8001-8003
for port in [8001, 8002, 8003]:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        if result == 0:
            print(f'Port {port} is in use, trying to free it...')
            # Try to find and kill the process
            os.system(f'taskkill /F /IM python.exe 2>nul')
            time.sleep(2)
    except:
        pass

# Start uvicorn server on a free port
port = 8002
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', f'--port', str(port)],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for server to start
time.sleep(3)

if proc.poll() is not None:
    print('ERROR: Server crashed!')
    print('STDERR:', proc.stderr.read())
    sys.exit(1)

print(f'Server started on port {port}')

conn = http.client.HTTPConnection('127.0.0.1', port)

results = []

# 1. /health
conn.request('GET', '/health')
resp = conn.getresponse()
body = resp.read().decode()
results.append(('/health', resp.status, body))
print(f'/health: Status {resp.status}')
print(f'  Body: {body[:80]}')

# 2. /api/meters/query?status=Installed
conn.request('GET', '/api/meters/query?status=Installed')
resp = conn.getresponse()
body = resp.read().decode()
try:
    data = json.loads(body)
    results.append(('/api/meters/query?status=Installed', resp.status, data.get('total', 'N/A')))
    print(f'/api/meters/query?status=Installed: Status {resp.status}')
    print(f'  Total: {data.get("total")}')
    print(f'  Meters count: {len(data.get("meters", []))}')
except Exception as e:
    results.append(('/api/meters/query?status=Installed', resp.status, f'Error: {e}'))
    print(f'/api/meters/query?status=Installed: Status {resp.status}')
    print(f'  Error: {e}')

# 3. /api/hierarchy?zone_code=Z-01
conn.request('GET', '/api/hierarchy?zone_code=Z-01')
resp = conn.getresponse()
body = resp.read().decode()
try:
    data = json.loads(body)
    results.append(('/api/hierarchy?zone_code=Z-01', resp.status, data.get('total_records', 'N/A')))
    print(f'/api/hierarchy?zone_code=Z-01: Status {resp.status}')
    print(f'  Zones: {list(data.get("zones", {}).keys())}')
    print(f'  Total records: {data.get("total_records")}')
except Exception as e:
    results.append(('/api/hierarchy?zone_code=Z-01', resp.status, f'Error: {e}'))
    print(f'/api/hierarchy?zone_code=Z-01: Status {resp.status}')
    print(f'  Error: {e}')

# 4. /api/metadata
conn.request('GET', '/api/metadata')
resp = conn.getresponse()
body = resp.read().decode()
try:
    data = json.loads(body)
    results.append(('/api/metadata', resp.status, data.get('record_count', 'N/A')))
    print(f'/api/metadata: Status {resp.status}')
    print(f'  Record count: {data.get("record_count")}')
    print(f'  Freshness policy: {data.get("freshness", {}).get("policy")}')
except Exception as e:
    results.append(('/api/metadata', resp.status, f'Error: {e}'))
    print(f'/api/metadata: Status {resp.status}')
    print(f'  Error: {e}')

# 5. /api/meters/nearby
conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5')
resp = conn.getresponse()
body = resp.read().decode()
try:
    data = json.loads(body)
    results.append(('/api/meters/nearby', resp.status, data.get('total', 'N/A')))
    print(f'/api/meters/nearby: Status {resp.status}')
    print(f'  Total: {data.get("total")}')
    print(f'  Meters count: {len(data.get("meters", []))}')
    if data.get('meters'):
        print(f'  Closest: {data["meters"][0]}')
except Exception as e:
    results.append(('/api/meters/nearby', resp.status, f'Error: {e}'))
    print(f'/api/meters/nearby: Status {resp.status}')
    print(f'  Error: {e}')

conn.close()
proc.terminate()
proc.wait()
print('\n--- SMOKE TEST SUMMARY ---')
for name, status, detail in results:
    print(f'{name}: Status {status} - {detail}')