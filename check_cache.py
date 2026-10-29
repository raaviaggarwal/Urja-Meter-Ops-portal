#!/usr/bin/env python3
import sys
sys.path.insert(0, ".")
from app import _hierarchy_cache

# Check cache structure
print("Cache keys:", list(_hierarchy_cache.keys()))
print("total_records:", _hierarchy_cache.get("total_records"))
print("zones type:", type(_hierarchy_cache.get("zones")))
print("zones count:", len(_hierarchy_cache.get("zones", {})))