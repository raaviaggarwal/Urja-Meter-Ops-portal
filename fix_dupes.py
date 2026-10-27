with open('app.py', 'r') as f:
    content = f.read()

# Find positions of _build_hierarchy
import re
positions = [m.start() for m in re.finditer(r'def _build_hierarchy', content)]
print(f'Positions of _build_hierarchy: {positions}')

# The second one is at positions[1]
pos = positions[1]
# Find 'return hierarchy' after this position
return_pos = content.find('return hierarchy', pos)
if return_pos >= 0:
    # Find the end: look for '# Build hierarchy once at startup' after return hierarchy
    build_marker = content.find('# Build hierarchy once at startup', return_pos)
    if build_marker >= 0:
        # Remove from pos to build_marker (including the '# Build hierarchy once at startup' line)
        new_content = content[:pos] + content[build_marker:]
        with open('app.py', 'w') as f:
            f.write(new_content)
        print(f'Removed second _build_hierarchy, saved from {pos} to {build_marker}')
    else:
        print('Could not find build marker after return hierarchy')
else:
    print('Could not find return hierarchy after second _build_hierarchy')