import sys
from setuptools import setup

if sys.version_info < (3,4):
    raise RuntimeError('Sorry, required python version 3.4 or later.')

setup(
    name = 'Aqua',
    author = 'Alexey Poryadin',
    author_email = 'alexey.poryadin@gmail.com',
    description = 'Async HTTP based on asyncio.',
)