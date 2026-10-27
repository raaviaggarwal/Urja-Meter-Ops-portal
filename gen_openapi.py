#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, '.')
from app import app

# Generate OpenAPI schema
schema = app.openapi()

# Write to file
with open('openapi.json', 'w') as f:
    json.dump(schema, f, indent=2)

print(f'openapi.json generated: {len(schema)} routes')
print(f'Routes in schema: {len(schema.get("paths", {}))} path items')

# List all paths
paths = schema.get('paths', {})
for path, methods in sorted(paths.items(), key=lambda x: x[0]):
    methods_str = ', '.join(methods.keys()) if methods else 'unknown'
    print(f'  {methods_str:15} {path}')