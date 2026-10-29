#!/usr/bin/env python3
# Patch TestClient to fix httpx 0.28.1 compatibility issue
import sys
sys.path.insert(0, '.')

from starlette.testclient import TestClient as OrigTestClient

original_init = OrigTestClient.__init__

def patched_init(self, app, base_url="http://testserver", **kwargs):
    try:
        original_init(self, app, base_url=base_url, **kwargs)
    except TypeError as e:
        if "unexpected keyword argument 'app'" in str(e):
            # Handle the incompatibility
            from starlette.testclient import _TestClientTransport
            from starlette._utils import _is_asgi3
            
            if _is_asgi3(app):
                asgi_app = app
            else:
                from starlette.applications import _WrapASGI2
                asgi_app = _WrapASGI2(app)
            
            self.app = asgi_app
            self.app_state = {}
            self.raise_server_exceptions = kwargs.get('raise_server_exceptions', True)
            self.base_url = base_url
            self.follow_redirects = kwargs.get('follow_redirects', True)
            self.cookies = kwargs.get('cookies')
            self.headers = {'user-agent': 'testclient'}
            
            # Create transport
            root_path = kwargs.get('root_path', '')
            self.transport = _TestClientTransport(
                self.app,
                portal_factory=self._portal_factory,
                raise_server_exceptions=self.raise_server_exceptions,
                root_path=root_path,
                app_state=self.app_state,
            )
            # Do NOT call super().__init__ with app parameter
            # The test client methods should still work via self.app and self.transport
        else:
            raise

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