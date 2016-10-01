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
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

from pystray import _base


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


class GtkIcon(_base.Icon):
    def __init__(self, *args, **kwargs):
        super(GtkIcon, self).__init__(*args, **kwargs)
        self._loop = None

    def _create_menu_handle(self):
        return self._create_menu(self.menu)

    def _run(self):
        self._loop = GLib.MainLoop.new(None, False)
        self._mark_ready()

        # Make sure that we do not inhibit ctrl+c
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self._loop.run()
        except:
            self._log.error(
                'An error occurred in the main loop', exc_info=True)
        finally:
            self._finalize()

    @mainloop
    def _stop(self):
        self._loop.quit()

    def _create_menu(self, descriptors):
        """Creates a :class:`Gtk.Menu` from a :class:`pystray.Menu` instance.

        :param descriptors: The menu descriptors. If this is falsy, ``None`` is
            returned.

        :return: a :class:`Gtk.Menu` or ``None``
        """
        if not descriptors:
            return None

        else:
            menu = Gtk.Menu.new()
            for descriptor in descriptors:
                menu.append(self._create_menu_item(descriptor))
            menu.show_all()

            return menu

    def _create_menu_item(self, descriptor):
        """Creates a :class:`Gtk.MenuItem` from a :class:`pystray.MenuItem`
        instance.

        :param descriptor: The menu item descriptor.

        :return: a :class:`Gtk.MenuItem`
        """
        if descriptor is _base.Menu.SEPARATOR:
            return Gtk.SeparatorMenuItem()

        else:
            if descriptor.checked is not None:
                menu_item = Gtk.CheckMenuItem.new_with_label(descriptor.text)
                menu_item.set_active(descriptor.checked)
                menu_item.set_draw_as_radio(descriptor.radio)
            else:
                menu_item = Gtk.MenuItem.new_with_label(descriptor.text)
            if descriptor.submenu:
                menu_item.set_submenu(self._create_menu(descriptor.submenu))
            else:
                menu_item.connect('activate', self._handler(descriptor))
            if descriptor.default:
                menu_item.get_children()[0].set_markup(
                    '<b>%s</b>' % GLib.markup_escape_text(descriptor.text))
            return menu_item

    def _finalize(self):
        """Removes all resources after :meth:`_run`.
        """
        pass
