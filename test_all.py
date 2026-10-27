import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Test /api/metadata
resp = client.get('/api/metadata')
print(f'Metadata: {resp.status_code}')
meta = resp.json()
print(f'  record_count: {meta.get("record_count")}')
print(f'  source_file: {meta.get("source_file")}')
print(f'  file_modification_time: {meta.get("file_modification_time")}')
print(f'  freshness policy: {meta.get("freshness", {}).get("policy")}')
print(f'  dataset phase_types: {meta.get("dataset", {}).get("phase_types")}')

# Test /api/meters/nearby with a known location
# Use a known meter's coordinates
resp = client.get('/api/meters')
meters_data = resp.json()
if meters_data.get('meters'):
    m = meters_data['meters'][0]
    mid = m['meterId']
    geo = m.get('geo')
    if geo and geo.get('lat') and geo.get('lng'):
        lat = geo['lat']
        lng = geo['lng']
        # Test nearby search with 5km radius
        resp2 = client.get(f'/api/meters/nearby?latitude={lat}&longitude={lng}&radius_km=5')
        print(f'Nearby search for meter {mid} at ({lat}, {lng}): {resp2.status_code}')
        if resp2.status_code == 200:
            data = resp2.json()
            print(f'  total: {data.get("total")}')
            print(f'  meters count: {len(data.get("meters", []))}')
            if data.get('meters'):
                print(f'  closest: {data["meters"][0]}')
    else:
        print(f'Meter {mid} has no geo data')

# Test all original endpoints still work
print()
print('=== Testing original endpoints ===')

resp = client.get('/api/meters')
print(f'/api/meters: {resp.status_code} - count: {len(resp.json().get("meters", []))}')

resp = client.get('/api/meters/search')
print(f'/api/meters/search: {resp.status_code}')

resp = client.get('/api/meters/status/Installed')
print(f'/api/meters/status/Installed: {resp.status_code} - count: {len(resp.json().get("meters", []))}')

resp = client.get('/api/meters/{meter_id}'.format(meter_id=meters_data['meters'][0]['meterId']) if meters_data.get('meters') else '/api/meters/search')
if meters_data.get('meters'):
    mid = meters_data['meters'][0]['meterId']
    resp = client.get(f'/api/meters/{mid}')
    print(f'/api/meters/{mid}: {resp.status_code}')

resp = client.get('/api/transformers')
print(f'/api/transformers: {resp.status_code}')

resp = client.get('/api/export/meters')
print(f'/api/export/meters: {resp.status_code}')

resp = client.get('/api/hierarchy')
print(f'/api/hierarchy: {resp.status_code}')

resp = client.get('/api/meters/query')
print(f'/api/meters/query: {resp.status_code}')

print()
print('All endpoint tests completed!')