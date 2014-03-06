#!/usr/bin/env python

from setuptools import setup

setup(
    name='geekcms',
    version='0.1',
    author='Zhan Haoxun',
    author_email='programmer.zhx@gmail.com',

    url='',
    license='MIT',
    description='',
    # long_description=open('README.rst').read(),

    # install_requires=[],
    packages=['geekcms'],
    # entry_points={
    #     'console_scripts': [
    #         'mgd = mgd.interface:main',
    #     ],
    # },
    test_suite='tests.test_protocal',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
