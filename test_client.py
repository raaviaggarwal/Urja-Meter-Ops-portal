#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from starlette.testclient import TestClient
import app as app_mod

try:
    client = TestClient(app_mod.app)
    print('Method 1: Success')
except TypeError as e:
    print(f'Method 1: Failed - {e}')

try:
    client = TestClient(app_mod.app, base_url='http://test')
    print('Method 2: Success')
except TypeError as e:
    print(f'Method 2: Failed - {e}')

import httpx
import inspect
sig = inspect.signature(httpx.Client.__init__)
params = list(sig.parameters.keys())
print(f'hpx.Client.__init__ params: {params}')
has_app = 'app' in params
print(f'Has app param: {has_app}')