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
import os
import signal
import tempfile

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
    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._loop = None
        self._status_icon = Gtk.StatusIcon.new()
        self._status_icon.connect('activate', lambda _: self.on_activate(self))

        if self.icon:
            self._update_icon()

    @mainloop
    def _show(self):
        self._status_icon.set_visible(True)

    @mainloop
    def _hide(self):
        self._status_icon.set_visible(False)

    @mainloop
    def _update_icon(self):
        # Write the buffered image to a file and set the status icon image from
        # the file
        fd, icon_path = tempfile.mkstemp('.png')
        try:
            with os.fdopen(fd, 'wb') as f:
                self.icon.save(f, format='PNG')
            self._status_icon.set_from_file(icon_path)

        finally:
            try:
                os.unlink(icon_path)
            except:
                pass

    @mainloop
    def _update_title(self):
        self._status_icon.set_title(self.title)

    def _run(self):
        self._loop = GLib.MainLoop.new(None, False)
        self._mark_ready()

        def sigint(*args):
            self._loop.quit()
            previous_sigint(*args)

        # Make sure that we do not inhibit ctrl+c
        previous_sigint = signal.signal(signal.SIGINT, sigint)
        try:
            self._loop.run()
        finally:
            if signal.getsignal(signal.SIGINT) == sigint:
                signal.signal(signal.SIGINT, previous_sigint)

    @mainloop
    def _stop(self):
        self._loop.quit()
