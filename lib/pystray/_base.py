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

import threading

from six.moves import queue


class Icon(object):
    """A representation of a system tray icon.

    The icon is initially hidden. Call :meth:`show` to show it.

    :param str name: The name of the icon. This is used by the system to
        identify the icon.

    :param icon: The icon to use. If this is specified, it must be a
        :class:`PIL.Image.Image` instance.

    :param str title: A short title for the icon.

    :param callable on_activate: A callback for when the system tray icon is
        activated. It is passed the icon as its sole argument.
    """
    def __init__(self, name, icon=None, title=None, on_activate=None):
        self._name = name

        if icon:
            self._icon = icon
        else:
            self._icon = None

        if title:
            self._title = title
        else:
            self._title = ''

        self._visible = False

        if on_activate:
            self.on_activate = on_activate
        else:
            self.on_activate = lambda icon: None

        self.__queue = queue.Queue()

        self._running = False

    def __del__(self):
        if self.visible:
            self._hide()

    @property
    def name(self):
        """The name passed to the constructor.
        """
        return self._name

    @property
    def icon(self):
        """The current icon.

        Setting this to a falsy value will hide the icon. Setting this to an
        image while the icon is hidden has no effect until the icon is shown
        using :meth:`show`.
        """
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        if value:
            if self.visible:
                self._update_icon()
        else:
            if self.visible:
                self.visible = False

    @property
    def title(self):
        """The current icon title.
        """
        return self._title

    @title.setter
    def title(self, value):
        if value != self._title:
            self._title = value
            if self.visible:
                self._update_title()

    @property
    def visible(self):
        """Whether the icon is currently visible.

        :raises ValueError: if set to ``True`` and no icon image has been set
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        if self._visible == value:
            return

        if value:
            if not self._icon:
                raise ValueError('cannot show icon without icon data')

            self._show()
            self._visible = True

        else:
            self._hide()
            self._visible = False

    def run(self, setup=None):
        """Enters the loop handling events for the icon.

        This method is blocking until :meth:`stop` is called. It *must* be
        called from the main thread.

        :param callable setup: An optional callback to execute in a separate
            thread once the loop has started. It is passed the icon as its sole
            argument.
        """
        def setup_handler():
            self.__queue.get()
            if setup:
                setup(self)

        self._setup_thread = threading.Thread(target=setup_handler)
        self._setup_thread.start()
        self._run()
        self._running = True

    def stop(self):
        """Stops the loop handling events for the icon.

        This method can be called either from the ``on_activate`` callback or
        from a different thread.
        """
        self._stop()
        if self._setup_thread.ident != threading.current_thread().ident:
            self._setup_thread.join()
        self._running = False

    def _mark_ready(self):
        """Marks the icon as ready.

        The setup callback passed to :meth:`run` will not be called until this
        method has been invoked.
        """
        self.__queue.put(True)

    def _show(self):
        """The implementation of the :meth:`show` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _hide(self):
        """The implementation of the :meth:`hide` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _update_icon(self):
        """Updates the image for an already shown icon.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _update_title(self):
        """Updates the title for an already shown icon.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _run(self):
        """Runs the event loop.

        This method must call :meth:`_mark_ready` once the loop is ready.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _stop(self):
        """Stops the event loop.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()
