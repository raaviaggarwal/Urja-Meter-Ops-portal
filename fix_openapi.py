#!/usr/bin/env python3
import json

with open('openapi.json', 'r') as f:
    data = json.load(f)

# Fix duplicate operation IDs
for path, methods in data.get('paths', {}).items():
    if path == '/api/meters-query':
        for method, details in methods.items():
            if details.get('operationId') == 'query_meters_api_meters_query_get':
                details['operationId'] = 'query_meters_api_meters_query_get_v2'
                print(f'Fixed /api/meters-query operation ID to: {details["operationId"]}')

with open('openapi.json', 'w') as f:
    json.dump(data, f, indent=2)

print('openapi.json fixed')