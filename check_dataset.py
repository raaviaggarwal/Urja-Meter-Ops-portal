from app import app, dataset, TOTAL_RECORDS
installed = app._by_status.get("Installed", [])
faulty = app._by_status.get("Faulty", [])
decommissioned = app._by_status.get("Decommissioned", [])
print(f'Dataset length: {len(dataset) if dataset else 0}')
print(f'TOTAL_RECORDS: {TOTAL_RECORDS}')
print(f'Installed count: {len(installed)}')
print(f'Faulty count: {len(faulty)}')
print(f'Decommissioned count: {len(decommissioned)}')