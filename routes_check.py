#!/usr/bin/env python3
from fastapi.applications import FastAPI
import sys
sys.path.insert(0, '.')
from app import app

print('=== ALL ROUTES WITH NAMES ===')
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = route.methods
        path = route.path
        name = getattr(route, 'name', 'unknown')
        method_str = str(sorted(list(methods)))
        print(f'  {method_str:20} {path:30} {name}')

print()
print('=== Checking if /api/meters/query has 2 routes ===')
query_routes = [r for r in app.routes if getattr(r, 'path', None) == '/api/meters/query']
print(f'Number of /api/meters/query routes: {len(query_routes)}')
for i, r in enumerate(query_routes):
    methods = list(r.methods)
    print(f'  Route {i}: methods={methods}, name={getattr(r, "name", "unknown")}')