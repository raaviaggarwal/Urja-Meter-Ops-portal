#!/usr/bin/env python3
import json, urllib.request

# Load the export data
with open('meter-export.json', 'r') as f:
    dataset = json.load(f)

# Build a lookup by meterId
by_id = {r['meterId']: r for r in dataset}

print('=== DATA CORRECTNESS: 3 meters comparison ===')
print()

# Pick 3 meters: one typical, one edge-case, one odd
meters_to_check = ['J100000', 'J100020', 'J100043']

for mid in meters_to_check:
    record = by_id.get(mid)
    if record:
        print(f'Meter {mid}:')
        print(f'  make={record["make"]}, phaseType={record["phaseType"]}, '
              f'installStatus={record["installStatus"]}, dtCode={record["dtCode"]}')
    else:
        print(f'Meter {mid}: NOT IN EXPORT')
print()

# Now fetch from API
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

print('=== API responses for same 3 meters ===')
for mid in meters_to_check:
    status, parsed, body = request('GET', f'/api/meters/{mid}')
    print(f'Meter {mid} from API:')
    if status == 200:
        rec = parsed
        make = rec.get('make', 'N/A')
        phase = rec.get('phaseType', 'N/A')
        status_rec = rec.get('installStatus', 'N/A')
        dt = rec.get('dtCode', 'N/A')
        print(f'  make={make}, phaseType={phase}, installStatus={status_rec}, dtCode={dt}')
    else:
        print(f'  Status: {status}, Response: {parsed}')
print()

# Check for differences
print('=== Differences between export and API ===')
for mid in meters_to_check:
    record = by_id.get(mid)
    if record:
        status, parsed, body = request('GET', f'/api/meters/{mid}')
        if status == 200:
            api_rec = parsed
            diffs = []
            for key in record.keys():
                if key in api_rec:
                    if record[key] != api_rec[key]:
                        diffs.append(f'  {key}: export={str(record[key])} api={str(api_rec[key])}')
            if diffs:
                print(f'Meter {mid}:')
                for d in diffs:
                    print(d)
            else:
                print(f'Meter {mid}: NO DIFFERENCES - data matches')
        else:
            print(f'Meter {mid}: API returned status {status}')