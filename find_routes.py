#!/usr/bin/env python3
with open('app.py', 'r') as f:
    lines = f.readlines()

# Search for "def get_hierarchy" 
for i, line in enumerate(lines, 1):
    if 'def get_hierarchy' in line:
        print(f'Line {i}: {line.rstrip()}')
        for j in range(i, min(i+6, len(lines))):
            print(f'  {j+1}: {lines[j][:100]}')
        print()