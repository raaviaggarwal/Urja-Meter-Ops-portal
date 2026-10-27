"""Test the query and nearby endpoints using http.client."""
import json
import subprocess
import sys
import time
import http.client

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
    results = []
    
    # Test query: Installed status
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?status=Installed')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('status=Installed', r.status, parsed.get('total')))
    conn.close()
    
    # Query: make=HPL
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?make=HPL')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('make=HPL', r.status, parsed.get('total')))
    conn.close()
    
    # Query: phase_type=single
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?phase_type=single')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('phase_type=single', r.status, parsed.get('total')))
    conn.close()
    
    # Query: multiple filters
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?status=Installed&make=HPL&phase_type=single')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('status+make+phase', r.status, parsed.get('total')))
    conn.close()
    
    # Query: dt_code=DT-001
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?dt_code=DT-001')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('dt_code=DT-001', r.status, parsed.get('total')))
    conn.close()
    
    # Query: zone_code=Z-01
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?zone_code=Z-01')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('zone_code=Z-01', r.status, parsed.get('total')))
    conn.close()
    
    # Query: pagination
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    conn.request('GET', '/api/meters/query?status=Installed&page=1&per_page=5')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('pagination', r.status, parsed.get('total'), len(parsed.get('meters', [])), parsed.get('page')))
    conn.close()
    
    # Print results
    for name, status, *rest in results:
        if rest:
            if len(rest) == 4:
                t, l, p = rest
                print(f'{name}: {status} total={t} len={l} page={p}')
            else:
                t = rest[0]
                print(f'{name}: {status} total={t}')
        else:
            print(f'{name}: {status}')
    
finally:
    proc.terminate()
    proc.wait()
    print('Server stopped')