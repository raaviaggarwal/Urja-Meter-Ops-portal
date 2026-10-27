"""Test the Flock Energy API endpoints using http.client."""
import http.client
import json
import subprocess
import sys
import time

PORT = 8000

def request(method, path):
    """Make an HTTP request to the running server."""
    conn = http.client.HTTPConnection('127.0.0.1', PORT, timeout=10)
    try:
        conn.request(method, path)
        r = conn.getresponse()
        body = r.read().decode()
        parsed = json.loads(body) if body else {}
        return r.status, parsed, body
    except Exception as e:
        return None, str(e), str(e)
    finally:
        conn.close()

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
    # Test health
    status, parsed, body = request('GET', '/health')
    print(f'Health: {status} {parsed}')
    
    # List meters
    status, parsed, body = request('GET', '/api/meters?page=1&per_page=2')
    print(f'List: {status} total={parsed.get("total")} meters={len(parsed.get("meters", []))} page={parsed.get("page")}')
    
    # Search by meter ID - try different queries
    print('--- Search tests ---')
    status, parsed, body = request('GET', '/api/meters/search?query=J100000')
    print(f'Search J100000: status={status} body={body}')
    
    status, parsed, body = request('GET', '/api/meters/search?query=Meter1')
    print(f'Search Meter1: status={status} body={body}')
    
    status, parsed, body = request('GET', '/api/meters/search?query=nonexistent')
    print(f'Search nonexistent: status={status} body={body}')
    
    # Status filter
    print('--- Status tests ---')
    status, parsed, body = request('GET', '/api/meters/status/Installed')
    print(f'Status Installed: {status} total={parsed.get("total")}')
    
    status, parsed, body = request('GET', '/api/meters/status/Faulty')
    print(f'Status Faulty: {status} total={parsed.get("total")}')
    
    status, parsed, body = request('GET', '/api/meters/status/Decommissioned')
    print(f'Status Decommissioned: {status} total={parsed.get("total")}')
    
    # Individual meter
    print('--- Individual meter tests ---')
    status, parsed, body = request('GET', '/api/meters/J100000')
    print(f'Meter J100000: {status} meterId={parsed.get("meterId")} status={parsed.get("installStatus")}')
    
    status, parsed, body = request('GET', '/api/meters/nonexistent-id')
    print(f'Meter nonexistent: {status} {parsed}')
    
    # Transformers
    print('--- Transformers ---')
    status, parsed, body = request('GET', '/api/transformers')
    print(f'Transformers: {status} total={parsed.get("total")}')
    
    # Export
    print('--- Export ---')
    status, parsed, body = request('GET', '/api/export/meters')
    print(f'Export: {status} count={parsed.get("count")}')
    
    # Invalid status
    print('--- Invalid status ---')
    status, parsed, body = request('GET', '/api/meters/status/Invalid')
    print(f'Status Invalid: {status} {parsed}')
    
finally:
    proc.terminate()
    proc.wait()
    print('Server stopped')