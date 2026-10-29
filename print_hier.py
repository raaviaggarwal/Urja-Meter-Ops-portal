#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
# Print lines 606-650
for i in range(605, 650):
    if i < len(lines):
        line = lines[i]
        line = line.replace('\u2192', '->')
        print('{:3d}: {}'.format(i+1, line[:120]))
PYEOF