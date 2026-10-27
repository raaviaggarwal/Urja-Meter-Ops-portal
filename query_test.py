#!/usr/bin/env python3
import urllib.request, json

def request(method, path):
    try:
        url = 'http://127.0.0.1:8000' + path
        r = urllib.request.urlopen(url, timeout=10)
        body = r.read().decode()
        parsed = json.loads(body) if body else {}
        return r.status, parsed, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        parsed = json.loads(body) if body else {}
        return e.code, parsed, body
    except Exception as e:
        return None, str(e), str(e)

print('=== /api/meters/query with various filters ===')

# status=Installed
status, parsed, body = request('GET', '/api/meters/query?status=Installed')
print(f'status=Installed: status={status}, total={parsed.get("total") if status==200 else "N/A"}')

# status=Faulty
status, parsed, body = request('GET', '/api/meters/query?status=Faulty')
print(f'status=Faulty: status={status}, total={parsed.get("total") if status==200 else "N/A"}')

# status=Decommissioned
status, parsed, body = request('GET', '/api/meters/query?status=Decommissioned')
print(f'status=Decommissioned: status={status}, total={parsed.get("total") if status==200 else "N/A"}')

# status=Installed with pagination
status, parsed, body = request('GET', '/api/meters/query?status=Installed&page=1&per_page=5')
print(f'status=Installed page=1 per_page=5: status={status}, total={parsed.get("total") if status==200 else "N/A"}, page={parsed.get("page") if status==200 else "N/A"}')

# No filters
status, parsed, body = request('GET', '/api/meters/query')
print(f'query with no filters: status={status}')