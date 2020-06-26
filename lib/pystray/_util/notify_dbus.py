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
import shutil
import tempfile

import gi
gi.require_version('DBus', '1.0')
gi.require_version('Gio', '2.0')
from gi.repository import GLib, Gio

#: The destination name.
DESTINATION = 'org.freedesktop.Notifications'

#: The destination path.
PATH = '/org/freedesktop/Notifications'


class Notifier(object):
    def __init__(self):
        self._connection = Gio.bus_get_sync(
            Gio.BusType.SESSION,
            None)
        self._notify = Gio.DBusProxy.new_sync(
            self._connection,
            0,
            None,
            DESTINATION,
            PATH,
            DESTINATION,
            None)
        self._nid = 0
        self._icon = None

    def notify(self, title, message, icon):
        """Displays a notification message.

        :param str title: The message title.

        :param str message: The actual message.

        :param str icon: The icon path.
        """
        # Make sure the file exists after having been updated by the Icon
        # instance
        if self._icon is None:
            self._icon = tempfile.mktemp('.png')

        self._nid = self._notify.call_sync(
            'Notify',
            GLib.Variant(
                '(susssasa{sv}i)',
                (
                    '',
                    self._nid,
                    shutil.copy(icon, self._icon),
                    title,
                    message,
                    [],
                    [],
                    0)),
            Gio.DBusCallFlags.NONE,
            -1,
            None).unpack()[0]

    def hide(self):
        """Hides the notification displayed by :meth:`notify`.
        """
        # Make sure to remove the temporary file
        if self._icon is not None:
            os.unlink(self._icon)
            self._icon = None

        self._notify.call_sync(
            'CloseNotification',
            GLib.Variant(
                '(u)',
                (
                    self._nid,
                )),
            Gio.DBusCallFlags.NONE,
            -1,
            None)
        self._nid = 0
