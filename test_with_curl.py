"""Start the server and test with curl."""
import subprocess
import time
import json
import sys

# Start the server
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd='C:\\Users\\raavi\\Documents\\GitHub\\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

try:
    # Test health
    import urllib.request
    r = urllib.request.urlopen('http://127.0.0.1:8000/health')
    print(f'Health: {r.status} {json.loads(r.read())}')
    
    # List meters (page 1, per_page 2)
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/meters?page=1&per_page=2')
    body = json.loads(r.read())
    print(f'List: {body[\"total\"]} total, {len(body[\"meters\"])} meters')
    
    # Search
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/meters/search?query=J100000')
    body = json.loads(r.read())
    print(f'Search: {body[\"total\"]} results')
    
    # Status filter
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/meters/status/Installed')
    body = json.loads(r.read())
    print(f'Status Installed: {body[\"total\"]} meters')
    
    # Individual meter
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/meters/J100000')
    body = json.loads(r.read())
    print(f'Meter J100000: meterId={body.get(\"meterId\")}')
    
    # Nonexistent meter
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8000/api/meters/nonexistent')
        print('Nonexistent: unexpected 200')
    except urllib.error.HTTPError as e:
        print(f'Nonexistent: {e.code} {e.read().decode()}')
    
    # Transformers
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/transformers')
    body = json.loads(r.read())
    print(f'Transformers: total={body[\"total\"]}')
    
    # Export
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/export/meters')
    body = json.loads(r.read())
    print(f'Export: count={body[\"count\"]}')
    
finally:
    proc.terminate()
    proc.wait()
    print('Server stopped')