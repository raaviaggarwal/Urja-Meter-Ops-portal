#!/usr/bin/env python3
# Fix TestClient compatibility with starlette 0.36.3 + httpx 0.28.1
# The issue: TestClient.__init__ passes 'app' to httpx.Client.__init__(),
# which doesn't accept 'app' in httpx 0.28.1

# Apply the patch BEFORE importing TestClient in tests.py
import sys

# Save the original TestClient.__init__
from starlette.testclient import TestClient as _OrigTestClient
_orig_init = _OrigTestClient.__init__

def _patched_init(self, app, base_url="http://testserver", **kwargs):
    """Patched init that handles the 'app' parameter incompatibility."""
    try:
        _orig_init(self, app, base_url=base_url, **kwargs)
    except TypeError as e:
        if "unexpected keyword argument 'app'" in str(e):
            # Manually set up TestClient without passing app to super
            # We need to set up the ASGI app and transport, AND the httpx.Client attributes
            
            # Set self.app first
            self.app = app
            self.app_state = {}
            self.raise_server_exceptions = kwargs.get('raise_server_exceptions', True)
            self.base_url = base_url
            self.follow_redirects = kwargs.get('follow_redirects', True)
            self.cookies = kwargs.get('cookies')
            self.headers = {'user-agent': 'testclient'}
            
            # Create transport
            from starlette.testclient import _TestClientTransport
            root_path = kwargs.get('root_path', '')
            self.transport = _TestClientTransport(
                self.app,
                portal_factory=self._portal_factory,
                raise_server_exceptions=self.raise_server_exceptions,
                root_path=root_path,
                app_state=self.app_state,
            )
            
            # Now set up the httpx.Client attributes that would normally be
            # set by super().__init__()
            # The _params attribute needs to be initialized
            self._params = {}
            self._cookies = self.cookies or {}
            self._headers = self.headers
            self._base_url = base_url
            self._raise_server_exceptions = self.raise_server_exceptions
            self._follow_redirects = self.follow_redirects
            
            print(f'TestClient patched successfully')
        else:
            raise
    else:
        # Original init succeeded, do nothing extra
        pass

# Apply the patch
_OrigTestClient.__init__ = _patched_init

# Now we can import TestClient and it will use the patched init
from starlette.testclient import TestClient

# Verify the patch works
import app as app_mod
try:
    client = TestClient(app_mod.app)
    print('TestClient created successfully with patched init!')
    response = client.get('/health')
    print(f'Health endpoint: status={response.status_code}')
    print(f'Health endpoint: body={response.json()}')
except Exception as e:
    print(f'TestClient failed: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()