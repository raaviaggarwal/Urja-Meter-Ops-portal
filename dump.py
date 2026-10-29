#!/usr/bin/env python3
with open('app.py', 'rb') as f:
    content = f.read()
idx = content.find(b'async def get_hierarchy')
# Show bytes from idx to idx+600
section = content[idx:idx+600]
for i in range(0, len(section), 16):
    hex_part = ' '.join('{:02x}'.format(b) for b in section[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in section[i:i+16])
    print('{:06x}: {:<48} {}'.format(idx+i, hex_part, ascii_part))
PYEOF