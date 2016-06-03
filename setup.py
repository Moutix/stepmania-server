#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

import smserver

setup(
    name='smserver',

    version=smserver.__version__,

    packages=find_packages(),

    author="Sélim Menouar",

    author_email="selim.menouar@rez-gif.supelec.fr",

    description="Stepmania server implementation",

    long_description=open('README.md').read(),

    include_package_data=True,

    url='http://github.com/ningirsu/stepmania-server',

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    scripts=['scripts/smserver'],

    license="MSI",

    data_files=[('/etc/smserver', ['cfg/conf.yml'])],
)
