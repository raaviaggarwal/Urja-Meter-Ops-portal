import subprocess, sys, time, json, http.client

PORT = 8001
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(PORT)],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

try:
    results = []
    
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?status=Installed')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('status=Installed', r.status, parsed.get('total')))
    conn.close()
    
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?dt_code=DT-001')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('dt_code=DT-001', r.status, parsed.get('total')))
    conn.close()
    
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query?zone_code=Z-01')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('zone_code=Z-01', r.status, parsed.get('total')))
    conn.close()
    
    for name, status, total in results:
        print(f'{name}: {status} total={total}')
        
finally:
    proc.terminate()
    proc.wait()
    print('Done')