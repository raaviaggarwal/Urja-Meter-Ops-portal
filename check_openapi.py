#!/usr/bin/env python3
import json
with open('openapi.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('Paths:')
for path, methods in data.get('paths', {}).items():
    for method, details in methods.items():
        op_id = details.get('operationId', 'N/A')
        print(f'  {method.upper()} {path} -> {op_id}')
print()
# Check for duplicate operation IDs
from collections import Counter
op_ids = []
for path, methods in data.get('paths', {}).items():
    for method, details in methods.items():
        op_id = details.get('operationId', '')
        if op_id:
            op_ids.append(op_id)
counts = Counter(op_ids)
duplicates = {k: v for k, v in counts.items() if v > 1}
print(f'Duplicate operation IDs: {duplicates}')