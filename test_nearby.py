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
    
    # Test nearby endpoint
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5')
    r = conn.getresponse()
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    results.append(('nearby 5km', r.status, parsed.get('total'), len(parsed.get('meters', []))))
    conn.close()
    
    # Test invalid latitude
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/nearby?latitude=100&longitude=75.830957&radius_km=5')
    r = conn.getresponse()
    body = r.read().decode()
    results.append(('invalid lat', r.status, body[:50]))
    conn.close()
    
    # Test invalid longitude
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=200&radius_km=5')
    r = conn.getresponse()
    body = r.read().decode()
    results.append(('invalid lng', r.status, body[:50]))
    conn.close()
    
    # Test excessive radius
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=999')
    r = conn.getresponse()
    body = r.read().decode()
    results.append(('excessive radius', r.status, body[:50]))
    conn.close()
    
    for name, status, *rest in results:
        if len(rest) == 2:
            print(f'{name}: {status} {rest[0]}')
        else:
            t, n, d = rest
            print(f'{name}: {status} total={t} meters={d}')
            
finally:
    proc.terminate()
    proc.wait()
    print('Done')