with open('app.py', 'r') as f:
    content = f.read()

import re
print("=== Route definitions ===")
for m in re.finditer(r'@app\.get\(["\']', content):
    start = m.start()
    end = min(len(content), start+50)
    print(content[start:end])