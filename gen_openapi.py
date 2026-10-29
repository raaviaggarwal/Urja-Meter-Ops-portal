#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from app import app

schema = app.openapi()
output_path = ROOT / "openapi.json"

output_path.write_text(
    json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

paths = schema.get('paths', {})
operation_count = sum(len(methods) for methods in paths.values())
print(f'openapi.json generated: {len(paths)} paths, {operation_count} operations')

for path, methods in sorted(paths.items(), key=lambda x: x[0]):
    methods_str = ', '.join(methods.keys()) if methods else 'unknown'
    print(f'  {methods_str:15} {path}')