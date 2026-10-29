#!/usr/bin/env python3
import sys

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace the general exception handler to log the exception to a file
old_handler = """@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    import traceback as tb
    with open('/tmp/app_error.log', 'w') as f:
        tb.print_exc(file=f)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )"""

new_handler = """@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    import traceback as tb
    with open('app_error.log', 'w') as f:
        tb.print_exc(file=f)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )"""

if old_handler in content:
    content = content.replace(old_handler, new_handler)
    with open('app.py', 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
    print("Handler modified successfully")
else:
    print("Could not find old handler")