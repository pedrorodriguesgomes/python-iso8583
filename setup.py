from setuptools import setup
from ISO8583.ISO8583 import __version__

setup(
    name='ISO8583',
    version=__version__,
    description='ISO8583 LIBRARY',
    author='Gia Duong Duc Minh',
    author_email='giaduongducminh@gmail.com',
    url='https://github.com/ducminhgd/python-ISOMessage8583',
    packages=['ISO8583'],
    keywords='ISO8583'
)
