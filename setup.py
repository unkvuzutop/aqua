import sys
from setuptools import setup

if sys.version_info < (3,4):
    raise RuntimeError('Sorry, required python version 3.4 or later.')

setup(
    name = 'Aqua',
    version = '0.1.5dev',
    package_dir = {'aqua': 'aqua'},
    author = 'Alexey Poryadin',
    author_email = 'alexey.poryadin@gmail.com',
    description = 'Async HTTP based on asyncio.',
    install_requires = [
        'webob'
    ],    
)