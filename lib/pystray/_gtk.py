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

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as AppIndicator
except:
    AppIndicator = None

from ._util import serialized_image
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
        self._status_icon.connect('activate', self._on_status_icon_activate)
        self._status_icon.connect('popup-menu', self._on_status_icon_popup_menu)
        self._popup_menu = None
        self._appindicator = None
        self._appindicator_icon_path = None

        if self.icon:
            self._update_icon()

    @mainloop
    def _show(self):
        self._status_icon.set_visible(True)

        if AppIndicator:
            self._appindicator = AppIndicator.Indicator.new(
                self.name,
                '',
                AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        else:
            self._appindicator = None

        if self._appindicator:
            self._status_icon.set_visible(False)
            self._appindicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self._appindicator.set_icon(self._appindicator_icon_path)

    @mainloop
    def _hide(self):
        self._status_icon.set_visible(False)

        if self._appindicator:
            self._appindicator = None

    @mainloop
    def _update_icon(self):
        # Write the buffered image to a file and set the status icon image from
        # the file
        with serialized_image(self.icon, 'PNG') as icon_path:
            self._status_icon.set_from_file(icon_path)

        self._remove_appindicator_icon()
        self._update_appindicator_icon()
        if self._appindicator:
            self._appindicator.set_icon(self._appindicator_icon_path)

    @mainloop
    def _update_title(self):
        self._status_icon.set_title(self.title)

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
            del self._appindicator
            self._remove_appindicator_icon()

    @mainloop
    def _stop(self):
        self._loop.quit()

    def _on_status_icon_activate(self, status_icon):
        """The handler for *activate* for the status icon.

        This signal handler will activate the icon.
        """
        self()

    def _on_status_icon_popup_menu(self, status_icon, button, activate_time):
        """The handler for *popup-menu* for the status icon.

        This signal handler will display the menu if one is set.
        """
        if self._menu_handle:
            self._menu_handle.popup(
                None, None, Gtk.StatusIcon.position_menu,
                self._status_icon, 0, Gtk.get_current_event_time())

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
            menu_item = Gtk.MenuItem.new_with_label(descriptor.text)
            menu_item.connect('activate', self._handler(descriptor))
            if descriptor.default:
                menu_item.get_children()[0].set_markup(
                    '<b>%s</b>' % GLib.markup_escape_text(descriptor.text))
            return menu_item

    def _remove_appindicator_icon(self):
        """Removes the temporary file used for the *AppIndicator*.
        """
        try:
            if self._appindicator_icon_path:
                os.unlink(self._appindicator_icon_path)
                self._appindicator_icon_path = None
        except:
            pass

    def _update_appindicator_icon(self):
        """Updates the *AppIndicator* icon.

        This method will update :attr:`_appindicator_icon_path` and create a new
        image file.

        If an *AppIndicator* icon is already set, call
        :meth:`_remove_appindicator_icon` first to ensure that the old file is
        removed.
        """
        self._appindicator_icon_path = tempfile.mktemp()
        with open(self._appindicator_icon_path, 'wb') as f:
            self.icon.save(f, 'PNG')
