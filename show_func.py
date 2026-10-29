#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
# Show the full get_hierarchy function
for i in range(805, 860):
    if i < len(lines):
        line = lines[i]
        print(f'{i+1}: {line[:120]}')