"""Simple test script."""
import subprocess, sys, time, json, http.client

PORT = 8001

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(PORT)],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

try:
    # Test /api/meters?status=Installed
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters?status=Installed')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'/api/meters?status=Installed: {r.status} total={json.loads(body).get("total")}')
    conn.close()
    
    # Test /api/meters/query with no params
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=5)
    conn.request('GET', '/api/meters/query')
    r = conn.getresponse()
    body = r.read().decode()
    print(f'/api/meters/query: {r.status} {body[:200]}')
    conn.close()
finally:
    proc.terminate()
    proc.wait()
    print('Done')