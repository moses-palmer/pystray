# coding=utf-8
# pystray
# Copyright (C) 2016-2020 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys


def backend():
    """Returns the backend module.
    """
    import importlib

    backend_name = os.environ.get('PYSTRAY_BACKEND', None)
    if backend_name:
        modules = [backend_name]
    elif sys.platform == 'darwin':
        modules = ['darwin']
    elif sys.platform == 'win32':
        modules = ['win32']
    else:
        modules = ['appindicator', 'gtk', 'xorg']

    errors = []
    for module in modules:
        try:
            return importlib.import_module(__package__ + '._' + module)
        except ImportError as e:
            errors.append(e)

    raise ImportError('this platform is not supported: {}'.format(
        '; '.join(str(e) for e in errors)))


Icon = backend().Icon
del backend

from ._base import Menu, MenuItem
