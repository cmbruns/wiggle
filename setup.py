#!/bin/env python

from setuptools import setup, find_packages

# Load module __version__ from wiggle/version.py
exec(open('wiggle/version.py').read())

setup(
    name='wiggle',
    version=__version__,
    author='Christopher Bruns',
    author_email='cmbruns@rotatingpenguin.com',
    description='wiggle 3D graphics and VR framework',
    url='https://github.com/cmbruns/wiggle',
    download_url='https://github.com/cmbruns/pyopenvr/tarball/' + __version__,
    license='GPL',
    packages=find_packages(),
    install_requires=['numpy', 'PyQt5'],
)
