""" Setup script """

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

CONF_DIR = None

if os.path.splitdrive(sys.executable)[0] != "":
    CONF_DIR = "conf"

if not CONF_DIR and os.path.isdir("/etc/smserver"):
    CONF_DIR = "/etc/smserver"

if not CONF_DIR:
    try:
        os.mkdir("/etc/smserver")
        CONF_DIR = "/etc/smserver"
    except:
        pass

if not CONF_DIR:
    CONF_DIR = "conf"

setup(
    name='smserver',

    version=smserver.__version__,

    packages=find_packages(),

    author="Sélim Menouar",

    author_email="selim.menouar@rez-gif.supelec.fr",

    description="An implementation of a Stepmania server",

    long_description=open('README.rst').read(),

    include_package_data=True,

    url='http://github.com/ningirsu/stepmania-server',

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    extras_require={
        ':python_version=="3.3"': ['asyncio', 'enum34'],
    },

    install_requires=[
        'pyyaml',
        'redis',
        'sqlalchemy',
        'websockets',
    ],

    scripts=['scripts/smserver'],

    console=['scripts/smserver'],

    options={
        "py2exe": {
            'packages': ['smserver'],
            "bundle_files": 0,
            "optimize": 2
        }
    },

    zipfile=None,

    license="MIT",

    data_files=[(CONF_DIR, ['cfg/conf.yml.orig'])],
)
