import sys
from setuptools import setup, find_packages

if sys.version_info < (3,4):
    raise RuntimeError('Sorry, required python version 3.4 or later.')

setup(
    name = 'AquaChat',
    version = '0.1',
    py_modules = ['aquachat'],
    include_package_data = True,
    install_requires = ['aqua', 'jinja2'],
)
