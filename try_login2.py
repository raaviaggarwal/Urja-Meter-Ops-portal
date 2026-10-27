import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get the login page first with proper headers
print("=== GET login page with browser UA ===")
req = urllib.request.Request('https://urja-ops.flockenergy.tech/login', 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
resp = urllib.request.urlopen(req, context=ctx)
html = resp.read().decode()

# Find the form action URL
form_start = html.find('<form')
if form_start >= 0:
    form_section = html[form_start:]
    # Look for action attribute
    action = re.search(r'action="([^"]*)"', form_section)
    method = re.search(r'method="([^"]*)"', form_section)
    print(f"Form action: {action.group(1) if action else 'not found'}")
    print(f"Form method: {method.group(1) if method else 'not found'}")

# Also check if there's any JavaScript that might handle the form submission
print("\nLooking for Svelte form handling patterns...")
if 'svelte' in html.lower():
    print("  Svelte framework detected")
    
# Submit the form
print("\n=== POST login ===")
data = urllib.parse.urlencode({'email': 'admin@flockenergy.com', 'password': 'admin'}).encode()
req = urllib.request.Request('https://urja-ops.flockenergy.tech/login', data=data, method='POST')
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
req.add_header('Origin', 'https://urja-ops.flockenergy.tech')
req.add_header('Referer', 'https://urja-ops.flockenergy.tech/login')
try:
    resp = urllib.request.urlopen(req, context=ctx)
    print("SUCCESS: " + str(resp.status))
    body = resp.read().decode()
    print("Response snippet: " + body[:300])
except urllib.error.HTTPError as e:
    print("HTTP Error: " + str(e.code))
    print("Response:", e.read().decode()[:300])
except Exception as e:
    print("Error: " + str(e))