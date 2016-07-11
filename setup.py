#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os
import sys
import glob

from setuptools import setup, find_packages
try:
    import py2exe
except ImportError:
    pass

import smserver

for filename in glob.glob("cfg/*.yml*"):
    shutil.copy(filename, "smserver/_fallback_conf")

conf_dir = None

if os.path.splitdrive(sys.executable)[0] != "":
    conf_dir = "conf"

if not conf_dir and os.path.isdir("/etc/smserver"):
    conf_dir = "/etc/smserver"

if not conf_dir:
    try:
        os.mkdir("/etc/smserver")
        conf_dir = "/etc/smserver"
    except:
        pass

if not conf_dir:
    conf_dir = "conf"

setup(
    name='smserver',

    version=smserver.__version__,

    packages=find_packages(),

    author="Sélim Menouar",

    author_email="selim.menouar@rez-gif.supelec.fr",

    description="An implementation of a Stepmania server",

    long_description=open('README.md').read(),

    include_package_data=True,

    url='http://github.com/ningirsu/stepmania-server',

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    extras_require={
        ':python_version=="3.3"': ['asyncio', 'enum34'],
    },

    install_requires=[
        'pyyaml',
        'sqlalchemy',
        'websockets',
    ],

    scripts=['scripts/smserver'],

    console=['scripts/smserver'],

    options={
        "py2exe": {
            'packages': ['smserver'],
            "bundle_files": 2,
        }
    },

    license="MSI",

    data_files=[(conf_dir, ['cfg/conf.yml.orig'])],
)
