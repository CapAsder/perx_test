import os

for _, _, files in os.walk('./app/resources/upload'):
    for file in files:
        exec(f'from .{file[:-3]} import {file[:-3]}')
    break
