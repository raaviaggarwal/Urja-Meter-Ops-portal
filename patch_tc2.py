#!/usr/bin/env python3
# Patch TestClient to fix httpx 0.28.1 compatibility
import sys
sys.path.insert(0, '.')

from starlette.testclient import TestClient as OrigTestClient
import starlette.testclient as testclient_module

# Store the original _TestClientTransport and _AsyncBackend
_orig_transport = testclient_module._TestClientTransport
_orig_backend = testclient_module._AsyncBackend

# Patch the TestClient.__init__ to fix httpx compatibility
original_init = OrigTestClient.__init__

def patched_init(self, app, base_url="http://testserver", **kwargs):
    # Call the original init but handle the TypeError for 'app' parameter
    try:
        original_init(self, app, base_url=base_url, **kwargs)
    except TypeError as e:
        if "unexpected keyword argument 'app'" in str(e):
            # Manually set up what TestClient needs
            # Process the app
            from starlette._utils import _is_asgi3
            from starlette.applications import _WrapASGI2
            
            if _is_asgi3(app):
                asgi_app = app
            else:
                asgi_app = _WrapASGI2(app)
            
            self.app = asgi_app
            self.app_state = {}
            
            # Set backend
            backend = kwargs.get('backend', 'asyncio')
            backend_options = kwargs.get('backend_options')
            self.async_backend = testclient_module._AsyncBackend(
                backend=backend, backend_options=backend_options or {}
            )
            
            # Set transport
            raise_server_exceptions = kwargs.get('raise_server_exceptions', True)
            root_path = kwargs.get('root_path', '')
            self.transport = _orig_transport(
                self.app,
                portal_factory=self._portal_factory,
                raise_server_exceptions=raise_server_exceptions,
                root_path=root_path,
                app_state=self.app_state,
            )
            
            # Set other attributes
            self.raise_server_exceptions = raise_server_exceptions
            self.base_url = base_url
            self.follow_redirects = kwargs.get('follow_redirects', True)
            self.cookies = kwargs.get('cookies')
            self.headers = {'user-agent': 'testclient'} if headers is None else headers
            
            # CRITICAL: Do NOT call super().__init__(app=self.app, ...)
            # Instead, directly configure the httpx.Client part
            # We need to set the transport and base_url on the Client
            # The parent httpx.Client.__init__ expects keyword args
            # but without 'app'
            
            # Set the transport directly on the instance
            self._transport = self.transport
            
            # Set base_url
            self.base_url = base_url
            
            # Set follow_redirects
            self.follow_redirects = self.follow_redirects
            
            # Set cookies
            self.cookies = self.cookies
            
            # Set default headers
            self._default_headers = self.headers
            
            # The test client methods (get, post, etc.) will use
            # self.app and self.transport to make requests
            # So we just need to make sure those are set correctly
            
            print(f'Patched TestClient for app: {app}')
        else:
            raise
    else:
        # Original init succeeded, do nothing extra
        pass

# Apply the patch
OrigTestClient.__init__ = patched_init

# Now try importing and using TestClient
import app as app_mod
try:
    client = OrigTestClient(app_mod.app)
    print('Patched TestClient created successfully!')
    response = client.get('/health')
    print(f'Health: status={response.status_code}')
    print(f'Health: body={response.json()}')
except Exception as e:
    print(f'Patched TestClient failed: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()