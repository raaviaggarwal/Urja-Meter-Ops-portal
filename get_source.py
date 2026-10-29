#!/usr/bin/env python3
import sys, importlib.util, inspect

spec = importlib.util.spec_from_file_location('app', 'app.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
src = inspect.getsource(mod.get_hierarchy)
print(src)