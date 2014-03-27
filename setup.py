#!/usr/bin/env python

from setuptools import setup, find_packages
from geekcms.interface import __version__

setup(
    name='geekcms',
    version=__version__,
    author='Zhan Haoxun',
    author_email='programmer.zhx@gmail.com',

    url='https://github.com/haoxun/GeekCMS',
    license='MIT',
    description='a lightweight framework for static site development',
    long_description=open('README.rst').read(),

    install_requires=['ply>=3.4', 'docopt'],
    packages=find_packages('geekcms'),
    entry_points={
        'console_scripts': [
            'geekcms = geekcms.interface:main',
        ],
    },
    test_suite='tests.load_tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
