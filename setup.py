#!/usr/bin/env python
# coding: utf-8

import os
import setuptools
import sys


#: The name of the package on PyPi
PYPI_PACKAGE_NAME = 'pystray'

#: The name of the main Python package
MAIN_PACKAGE_NAME = 'pystray'

#: The package URL
PACKAGE_URL = 'https://github.com/moses-palmer/pystray'

#: The author email
AUTHOR_EMAIL = 'moses.palmer@gmail.com'

#: The runtime requirements
RUNTIME_PACKAGES = [
    'Pillow',
    'six']

#: Additional requirements used during setup
SETUP_PACKAGES = RUNTIME_PACKAGES + [
    'sphinx >=1.3.1']

#: Packages requires for different environments
EXTRA_PACKAGES = {
    ':sys_platform == "darwin"': [
        'pyobjc-framework-Quartz >=7.0'],
    ':sys_platform == "linux"': [
        'python-xlib >=0.17']}


# Read globals from ._info without loading it
INFO = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        MAIN_PACKAGE_NAME,
        '_info.py'), 'rb') as f:
    data = (
        f.read().decode('utf-8') if sys.version_info.major >= 3
        else f.read())
    code = compile(data, '_info.py', 'exec')
    exec(code, {}, INFO)
INFO['author'] = INFO['__author__']
INFO['version'] = '.'.join(str(v) for v in INFO['__version__'])



# Load the read me
try:
    with open(os.path.join(
            os.path.dirname(__file__),
            'README.rst', 'rb')) as f:
        README = f.read().decode('utf-8')

    with open(os.path.join(
            os.path.dirname(__file__),
            'docs',
            'usage.rst'), 'rb') as f:
        README += '\n\n' + f.read().decode('utf-8')
except IOError:
    README = ''


# Load the release notes
try:
    with open(os.path.join(
            os.path.dirname(__file__),
            'CHANGES.rst'), 'rb') as f:
        CHANGES = f.read().decode('utf-8')
except IOError:
    CHANGES = ''


setuptools.setup(
    name=PYPI_PACKAGE_NAME,
    version=INFO['version'],
    description='Provides systray integration',
    long_description=README + '\n\n' + CHANGES,

    install_requires=RUNTIME_PACKAGES,
    setup_requires=RUNTIME_PACKAGES + SETUP_PACKAGES,
    extras_require=EXTRA_PACKAGES,

    author=INFO['author'],
    author_email=AUTHOR_EMAIL,

    url=PACKAGE_URL,

    packages=setuptools.find_packages(
        os.path.join(
            os.path.dirname(__file__),
            'lib')),
    package_dir={'': 'lib'},
    zip_safe=True,

    test_suite='tests',

    license='LGPLv3',
    keywords='system tray icon, systray icon',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 '
        '(LGPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'])
