import os

from app import api

for _, _, files in os.walk('./app/resources/upload'):
    for file in files:
        exec(f'from .upload import {file[:-3]}')
    break

lst = set(dir())
used = set()
used_routes = set()
for cls in lst:
    _ = eval(cls)
    if getattr(_, '__route__', False) and _.__name__ not in used:
        if _.__route__ in used_routes:
            raise RuntimeError("Re-using route: " + _.__route__)
        used_routes.add(_.__route__)
        used.add(_.__name__)
        api.add_resource(_, _.__route__)
