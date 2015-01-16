#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='geekcms',
    version='0.3',
    author='Zhan Haoxun',
    author_email='programmer.zhx@gmail.com',

    url='https://github.com/haoxun/GeekCMS',
    license='MIT',
    description='a lightweight framework for static site development.',
    long_description=open('README.rst').read(),

    install_requires=['ply>=3.4', 'docopt'],

    packages=['geekcms', 'geekcms.parser'],
    entry_points={
        'console_scripts': [
            'geekcms = geekcms.interface:main',
        ],
    },
    test_suite='tests.load_tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
