#!/usrusr/bin/env python3
import subprocess, sys, time, urllib.request, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8000', '--reload'],
    cwd=r'C:\Users\raavi\Documents\GitHub\Urja-Meter-Ops-portal',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Test with valid zone code
try:
    url = 'http://127.0.0.1:8000/api/hierarchy?zone_code=Z-01'
    print(f'Requesting: {url}')
    r = urllib.request.urlopen(url, timeout=10)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'HTTP Error status: {e.code}')
    print(f'Error body: {body}')
    # Try to get more detail
    try:
        import traceback
        print('Traceback:')
        # Try to get detailed error
    except:
        pass
except Exception as e:
    print(f'Other error: {type(e).__name__}: {e}')

# Also test without zone_code
try:
    url = 'http://127.0.0.1:8000/api/hierarchy'
    print(f'\nRequesting: {url}')
    r = urllib.request.urlopen(url, timeout=10)
    body = r.read().decode()
    parsed = json.loads(body) if body else {}
    print(f'Status: {r.status}')
    print(f'Zones: {list(parsed.get("zones", {}).keys())}')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'HTTP Error status: {e.code}')
    print(f'Error body: {body}')

proc.terminate()
proc.wait()
print('Done')