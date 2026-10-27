"""Minimal test script for the Flock Energy API."""
import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Test health
r = client.get('/health')
s = r.status_code
j = r.json()
print(f'Health: {s} {j}')

# Test listing
r = client.get('/api/meters?page=1&per_page=2')
s = r.status_code
m = len(r.json()['meters'])
print(f'List page 1/2: {s} {m} meters')

# Test search
r = client.get('/api/meters/search?query=J100000')
s = r.status_code
t = r.json()['total']
print(f'Search: {s} {t} results')

# Test status filter
r = client.get('/api/meters/status/Installed')
s = r.status_code
t = r.json()['total']
print(f'Status Installed: {s} {t} meters')

# Test individual meter
mid = 'J100000'
r = client.get(f'/api/meters/{mid}')
s = r.status_code
print(f'Meter {mid}: {s}')

# Test nonexistent
r = client.get('/api/meters/nonexistent')
s = r.status_code
print(f'Nonexistent: {s}')

# Test export
r = client.get('/api/export/meters')
s = r.status_code
c = r.json()['count']
print(f'Export: {s} count={c}')

# Test transformers
r = client.get('/api/transformers')
s = r.status_code
t = r.json()['total']
print(f'Transformers: {s} total={t}')

print('All tests done')