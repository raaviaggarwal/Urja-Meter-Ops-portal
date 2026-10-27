import re

with open('app.py', 'r') as f:
    content = f.read()

print('All @app.get routes:')
for m in re.finditer(r'@app\.get\(["\']', content):
    start = m.start()
    end = min(len(content), start+40)
    print(content[start:end])

print()
print('=== Check for /api/metadata ===')
if '/api/metadata' in content:
    print('Metadata route found')
else:
    print('Metadata route NOT found')

print()
print('=== Check for nearby_meters ===')
if 'nearby_meters' in content:
    print('nearby_meters function found')
else:
    print('nearby_meters function NOT found')

print()
print('=== Check for /api/meters/nearby ===')
if '/api/meters/nearby' in content:
    print('nearby route found')
else:
    print('nearby route NOT found')