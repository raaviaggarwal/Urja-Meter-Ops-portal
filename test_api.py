"""Minimal test script for the Flock Energy API."""
import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Test health
r = client.get('/health')
print(f'Health: {r.status_code} {r.json()}')

# Test listing
r = client.get('/api/meters?page=1&per_page=2')
print(f'List page 1/2: {r.status_code} {len(r.json()[\"meters\"])} meters')

# Test search
r = client.get('/api/meters/search?query=J100000')
print(f'Search: {r.status_code} {r.json()[\"total\"]} results')

# Test status filter
r = client.get('/api/meters/status/Installed')
print(f'Status Installed: {r.status_code} {r.json()[\"total\"]} meters')

# Test individual meter
mid = 'J100000'
r = client.get(f'/api/meters/{mid}')
print(f'Meter {mid}: {r.status_code}')

# Test nonexistent
r = client.get('/api/meters/nonexistent')
print(f'Nonexistent: {r.status_code}')

# Test export
r = client.get('/api/export/meters')
print(f'Export: {r.status_code} count={r.json()[\"count\"]}')

# Test transformers
r = client.get('/api/transformers')
print(f'Transformers: {r.status_code} total={r.json()[\"total\"]}')

print('All tests done')