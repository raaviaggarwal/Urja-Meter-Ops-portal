#!/usr/bin/env python3
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find list_meters - look for the @app.get decorator and function
for i in range(len(lines)):
    line = lines[i]
    if '@app.get' in line and '/api/meters' in line:
        # Print the decorator and next few lines
        print(f'Line {i+1}: {line.rstrip()}')
        for j in range(i+1, min(i+8, len(lines))):
            print(f'Line {j+1}: {lines[j][:80]}')
        print('---')