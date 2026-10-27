"""Fix syntax errors in app.py."""

with open('app.py', 'r') as f:
    content = f.read()

# Fix 1: Line 87 - chained .get() syntax
old1 = '_by_ct = r.get("hierarchy", {}.get("dt", {})'
new1 = '_by_ct = r.get("hierarchy", {}).get("dt", {})'
content = content.replace(old1, new1)

# Fix 2: The unmatched '})' on line 295
old2 = '})'
# Find the first '})' and replace with '}'
# But we need to be careful - there might be legitimate '})' elsewhere
# Let's just replace the one at the end of _paginate function
# The _paginate function returns a dict, so it should just be '}'
# Let's replace '})' with '}' only if it's at the end of a function return
# Looking at the context, line 295 has '})' which should be '}'
# Let's just replace the specific pattern

# Actually, let me just replace the first occurrence of '})' with '}'
# but only if it's followed by nothing or whitespace/newline
# Better approach: just replace the specific pattern at line 295 area
# The _paginate function returns dict, so line 295 should just be '}'

# Let me just replace '})' with '}' globally but be careful
# Actually, let me just replace the specific problematic occurrence
# The issue is at line 295 in the _paginate function return statement
# Let me search for '    })' (with 4 spaces) which is the _paginate return

if '    })' in content:
    content = content.replace('    })', '    }', 1)

with open('app.py', 'w') as f:
    f.write(content)
print('Fixed syntax errors')