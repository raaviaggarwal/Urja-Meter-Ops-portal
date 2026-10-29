#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient as _RawTestClient

# Apply monkey-patch BEFORE importing TestClient
from starlette.testclient import TestClient as _OrigTestClient
_orig_init = _OrigTestClient.__init__

def _patched_init(self, app, base_url="http://testserver", **kwargs):
    try:
        _orig_init(self, app, base_url=base_url, **kwargs)
    except TypeError as e:
        if "unexpected keyword argument 'app'" in str(e):
            self.app = app
            self.app_state = {}
            self.raise_server_exceptions = kwargs.get('raise_server_exceptions', True)
            self.base_url = base_url
            self.follow_redirects = kwargs.get('follow_redirects', True)
            self.cookies = kwargs.get('cookies')
            self.headers = {'user-agent': 'testclient'}
            from starlette.testclient import _TestClientTransport
            root_path = kwargs.get('root_path', '')
            self.transport = _TestClientTransport(
                self.app,
                portal_factory=lambda: None,
                raise_server_exceptions=self.raise_server_exceptions,
                root_path=root_path,
                app_state=self.app_state,
            )
            self._params = {}
            self._cookies = self.cookies or {}
            self._headers = self.headers
            self.base_url = base_url
            self._raise_server_exceptions = self.raise_server_exceptions
            self._follow_redirects = self.follow_redirects
        else:
            raise
_OrigTestClient.__init__ = _patched_init

from fastapi import FastAPI, Query, HTTPException

app = FastAPI(title='Test', response_model=None)

_hierarchy_cache = {
    'zones': {
        'Jaipur Zone 1': {
            'code': 'Z-01',
            'circles': {
                'Circle 1': {
                    'name': 'Circle 1',
                    'code': 'C-01',
                    'divisions': {
                        'Division 1': {
                            'name': 'Division 1',
                            'code': 'D-01',
                            'subdivisions': {
                                'Subdivision 1': {
                                    'name': 'Subdivision 1',
                                    'code': 'SD-01',
                                    'substations': {
                                        'Substation 1': {
                                            'name': 'Substation 1',
                                            'code': 'SS-01',
                                            'feeders': {
                                                'Feeder 1': {
                                                    'name': 'Feeder 1',
                                                    'code': 'F-001',
                                                    'dts': {
                                                        'Malviya Nagar DT 1': {
                                                            'name': 'Malviya Nagar DT 1',
                                                            'code': 'DT-001',
                                                            'meterCount': 10,
                                                            'meterIds': ['J100000', 'J100040', 'J100080']
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'total_records': 403
}

@app.get('/api/hierarchy', response_model=dict)
async def get_hierarchy(zone_code=None):
    if zone_code:
        zones = _hierarchy_cache.get('zones', {})
        matching_zone = None
        matching_zone_name = None
        for z_name, z_data in zones.items():
            if z_data.get('code') == zone_code or z_name.replace(' ', '') == zone_code.replace('Z-', ''):
                matching_zone = z_data
                matching_zone_name = z_name
                break
        if matching_zone is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zone with code '{zone_code}' not found",
            )
        return {
            'zones': {matching_zone_name: matching_zone},
            'total_records': _hierarchy_cache['total_records'],
        }
    return {
        'zones': _hierarchy_cache['zones'],
        'total_records': _hierarchy_cache['total_records'],
    }

client = _RawTestClient(app)

# Test 1: no params
print('Test 1: /api/hierarchy (no params)')
r = client.get('/api/hierarchy')
print(f'  Status: {r.status_code}, Body: {r.text[:200]}')

# Test 2: zone_code=Z-01
print('Test 2: /api/hierarchy?zone_code=Z-01')
r = client.get('/api/hierarchy?zone_code=Z-01')
print(f'  Status: {r.status_code}, Body: {r.text[:200]}')

# Test 3: zone_code=Z-99 (not found)
print('Test 3: /api/hierarchy?zone_code=Z-99')
r = client.get('/api/hierarchy?zone_code=Z-99')
print(f'  Status: {r.status_code}, Body: {r.text[:200]}')