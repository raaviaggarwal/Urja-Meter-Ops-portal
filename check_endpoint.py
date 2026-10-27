from app import app
import json, warnings
warnings.filterwarnings('ignore')

spec = app.openapi()
if '/api/meters/query' in spec.get('paths', {}):
    path_item = spec['paths']['/api/meters/query']
    get_op = path_item.get('get', {})
    print('Query endpoint parameters:')
    for param in get_op.get('parameters', []):
        pname = param.get('name', '')
        pdesc = param.get('description', '')
        print(f'  {pname}: {pdesc}')