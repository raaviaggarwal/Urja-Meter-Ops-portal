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

# Quick smoke test
s, p, b = request('GET', '/health')
print(f'Health: {s} {p}')

s, p, b = request('GET', '/api/meters')
print(f'Meters: {s} total={p.get("total")}')

s, p, b = request('GET', '/api/meters/search?query=J100000')
print(f'Search: {s} total={p.get("total")}')

s, p, b = request('GET', '/api/meters/status/Installed')
print(f'Status: {s} total={p.get("total")}')

s, p, b = request('GET', '/api/meters/J100000')
print(f'Meter: {s}')

s, p, b = request('GET', '/api/transformers')
print(f'Transformers: {s} total={p.get("total")}')

s, p, b = request('GET', '/api/export/meters')
print(f'Export: {s} count={p.get("count")}')

s, p, b = request('GET', '/api/hierarchy')
print(f'Hierarchy: {s}')

s, p, b = request('GET', '/api/metadata')
print(f'Metadata: {s} count={p.get("record_count")}')

s, p, b = request('GET', '/api/meters/nearby?latitude=26.938961&longitude=75.830957&radius_km=5')
print(f'Nearby: {s} total={p.get("total")}')

s, p, b = request('GET', '/api/meters/nonexistent')
print(f'Nonexistent: {s}')

s, p, b = request('GET', '/api/meters/unknown-meter-id')
print(f'Unknown: {s} {p}')