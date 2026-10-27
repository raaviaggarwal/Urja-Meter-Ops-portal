"""Debug the query endpoint."""
import subprocess
import sys
import time
import json
import http.client

PORT = 8001

# Start server
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(PORT)],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

try:
    # Test health first
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/health')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'Health: {r.status} {body}')
    conn.close()
    
    # Test query endpoint
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?status=Installed')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'Query status=Installed: {r.status}')
    print(f'Body: {body[:300]}')
    conn.close()
    
    # Test dt_code
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?dt_code=DT-001')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'Query dt_code=DT-001: {r.status} body={body[:300]}')
    conn.close()
    
    # Test zone_code
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?zone_code=Z-01')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'Query zone_code=Z-01: {r.status} body={body[:300]}')
    conn.close()
finally:
    proc.terminate()
    proc.wait()
    print('Done')