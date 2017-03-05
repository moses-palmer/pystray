# coding=utf-8
# pystray
# Copyright (C) 2016-2017 Moses Palmér
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


if os.environ.get('__PYSTRAY_GENERATE_DOCUMENTATION') == 'yes':
    from ._base import Icon
else:
    Icon = None


error = None
try:
    if sys.platform == 'darwin':
        if not Icon:
            from ._darwin import Icon

    elif sys.platform == 'win32':
        if not Icon:
            from ._win32 import Icon

    else:
        try:
            if not Icon:
                from ._appindicator import Icon
        except Exception as e:
            error = e
        try:
            if not Icon:
                from ._gtk import Icon
        except Exception as e:
            error = e
        try:
            if not Icon:
                from ._xorg import Icon
        except Exception as e:
            error = e


    if not Icon:
        if error:
            raise error
        else:
            raise ImportError('this platform is not supported')

finally:
    del error


from ._base import Menu, MenuItem
