# coding=utf-8
# pystray
# Copyright (C) 2016 Moses Palmér
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

import functools

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

from . import _base


def mainloop(f):
    """Marks a function to be executed in the main loop.

    The function will be sceduled to be executed later in the mainloop.

    :param callable f: The function to execute. Its return value is discarded.
    """
    @functools.wraps(f)
    def inner(*args, **kwargs):
        def callback(*args, **kwargs):
            """A callback that executes  ``f`` and then returns ``False``.
            """
            try:
                f(*args, **kwargs)
            finally:
                return False

        # Execute the callback as an idle function
        GObject.idle_add(callback, *args, **kwargs)

    return inner


class Icon(_base.Icon):
    @mainloop
    def _show(self):
        # TODO: Implement
        pass

    @mainloop
    def _hide(self):
        # TODO: Implement
        pass

    @mainloop
    def _update_icon(self):
        # TODO: Implement
        pass

    @mainloop
    def _update_title(self):
        # TODO: Implement
        pass

    def _run(self):
        # TODO: Implement
        pass

    @mainloop
    def _stop(self):
        # TODO: Implement
        pass
