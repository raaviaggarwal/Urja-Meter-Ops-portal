import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get the login page and examine all hidden fields
print("=== GET login page ===")
req = urllib.request.Request('https://urja-ops.flockenergy.tech/login')
resp = urllib.request.urlopen(req, context=ctx)
html = resp.read().decode()

# Find all input fields
inputs = re.findall(r'<input[^>]+>', html)
print("All input fields:")
for i in inputs:
    # Extract name and type
    name = re.search(r'name="([^"]+)"', i)
    typ = re.search(r'type="([^"]+)"', i)
    val = re.search(r'value="([^"]*)"', i)
    print(f"  name={name.group(1) if name else 'None'}, type={typ.group(1) if typ else 'None'}, value={val.group(1) if val else 'None'}")

# Also look for any other tags that might have hidden values
print("\nLooking for any value attributes in the form area...")
vals = re.findall(r'value="([^"]*)"', html)
print("All values found:", vals[:30])