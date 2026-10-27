"""Test the hierarchy endpoint."""
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
    
    # Test health first
    conn.request('GET', '/health')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'Health: {r.status} {json.loads(body) if body else {}}')
    
    # Test hierarchy endpoint (no filter)
    conn.request('GET', '/api/hierarchy')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'\\nHierarchy (no filter): status={r.status}')
    print(f"  total_records: {parsed.get('total_records')}")
    zones = parsed.get('zones', {})
    print(f"  zones count: {len(zones)}")
    for z_name, z_data in list(zones.items())[:3]:
        print(f"    Zone: {z_name}, code: {z_data.get('code')}, circles: {len(z_data.get('circles', {}))}")
    
    # Test hierarchy endpoint with zone filter
    conn.request('GET', '/api/hierarchy?zone_code=Z-01')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'\\nHierarchy (zone=Z-01): status={r.status}')
    zones = parsed.get('zones', {})
    for z_name, z_data in zones.items():
        print(f"  Zone: {z_name}, code: {z_data.get('code')}")
        circles = z_data.get('circles', {})
        print(f"    Circles: {len(circles)}")
        for c_name, c_data in list(circles.items())[:2]:
            print(f"      Circle: {c_name}, code: {c_data.get('code')}, divisions: {len(c_data.get('divisions', {}))}")
            divs = c_data.get('divisions', {})
            for d_name, d_data in list(divs.items())[:1]:
                print(f"        Division: {d_name}, code: {d_data.get('code')}, substations: {len(d_data.get('substations', {}))}")
    
    # Test 404 for bad zone code
    conn.request('GET', '/api/hierarchy?zone_code=Z-99')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'\\nHierarchy (zone=Z-99): status={r.status}')
    print(f'  body: {body}')
    
finally:
    proc.terminate()
    proc.wait()
    print('\\nServer stopped')