#!/usr/bin/env python3
with open('app.py', 'r') as f:
    content = f.read()
import re
matches = re.finditer(r'class MeterHierarchyTree', content)
for m in matches:
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 200)
    print(content[start:end])
    print("---")