"""Verify that app.py contains all documented routes."""
with open('app.py') as f:
    content = f.read()

routes = [
    ('/health', 'health'),
    ('/api/meters', 'list_meters'),
    ('/api/meters/{meter_id}', 'get_meter'),
    ('/api/meters/search', 'search_meters'),
    ('/api/meters/status/{status}', 'list_meters_by_status'),
    ('/api/transformers', 'list_transformers'),
    ('/api/export/meters', 'export_meters'),
]

print('Route verification:')
for route, name in routes:
    found = route in content
    print(f'  {name}: {"FOUND" if found else "MISSING"} ({route})')

print()
print('All routes verified.' if all(route in content for _, route in routes) else 'Some routes MISSING!')