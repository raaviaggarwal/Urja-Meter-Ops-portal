"""Test the query and nearby endpoints."""
import http.client
import json
import subprocess
import sys
import time

PORT = 8000

# Start the server
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(PORT)],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

try:
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    
    # Test query: Installed status
    conn.request('GET', '/api/meters/query?status=Installed')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query status=Installed: {r.status} total={parsed.get("total")}')
    
    # Query: make=HPL
    conn.request('GET', '/api/meters/query?make=HPL')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query make=HPL: {r.status} total={parsed.get("total")}')
    
    # Query: phase_type=single
    conn.request('GET', '/api/meters/query?phase_type=single')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query phase_type=single: {r.status} total={parsed.get("total")}')
    
    # Query: multiple filters
    conn.request('GET', '/api/meters/query?status=Installed&make=HPL&phase_type=single')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query status=Installed&make=HPL&phase_type=single: {r.status} total={parsed.get("total")}')
    
    # Query: dt_code=DT-001
    conn.request('GET', '/api/meters/query?dt_code=DT-001')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query dt_code=DT-001: {r.status} total={parsed.get("total")}')
    
    # Query: zone_code=Z-01
    conn.request('GET', '/api/meters/query?zone_code=Z-01')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query zone_code=Z-01: {r.status} total={parsed.get("total")}')
    
    # Query: empty circle_code
    conn.request('GET', '/api/meters/query?circle_code=')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query circle_code=empty: {r.status} total={parsed.get("total")}')
    
    # Query: pagination
    conn.request('GET', '/api/meters/query?status=Installed&page=1&per_page=5')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Query status=Installed page=1 per_page=5: {r.status} total={parsed.get("total")} len={len(parsed.get("meters", []))} page={parsed.get("page")}')
    
finally:
    proc.terminate()
    proc.wait()
    print('Server stopped')