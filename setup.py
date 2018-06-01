# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='py_zaif_websocket',
    packages=['py_zaif_websocket'],
    version='0.0.1',
    description="Python wrapper for zaif's Stream(WebSocket) API",
    long_description=readme,
    author='Mottio Cancer',
    author_email='mottio.cancer@gmail.com',
    url='https://github.com/mottio-cancer/py_zaif_websocket',
    install_requires=['websocket','websocket-client'],
    keywords=["bitcoin", "zaif", "wrapper", "Stream API", "websocket"],
    license=license
)

