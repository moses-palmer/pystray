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

import itertools
import logging
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

    :param menu: A menu to use as popup menu. This can be either an instance of
        :class:`Menu` or a tuple, which will be interpreted as arguments to the
        :class:`Menu` constructor.

        The behaviour of the menu depends on the platform. Only one action is
        guaranteed to be invokable: the first menu item whose
        :attr:`~pystray.MenuItem.default` attribute is set.

        Some platforms allow both menu interaction and a special way of
        activating the default action, some platform allow only either an
        invisible menu with a default entry as special action or a full menu
        with no special way to activate the default item, and some platforms do
        not support a menu at all.
    """
    def __init__(
            self, name, icon=None, title=None, menu=None):
        self._name = name
        self._icon = icon or None
        self._title = title or ''
        self._visible = False
        self._log = logging.getLogger(__name__)

        if menu:
            self._menu = menu if isinstance(menu, Menu) else Menu(*menu)
        else:
            self._menu = None

        self._running = False
        self.__queue = queue.Queue()

    def __del__(self):
        if self.visible:
            self._hide()

    def __call__(self):
        if self._menu is not None:
            self._menu(self)

    @property
    def name(self):
        """The name passed to the constructor.
        """
        return self._name

    @property
    def icon(self):
        """The current icon.

        Setting this to a falsy value will hide the icon. Setting this to an
        image while the icon is hidden has no effect until the icon is shown.
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
    def menu(self):
        """The menu.

        Setting this to a falsy value will disable the menu.
        """
        return self._menu

    @menu.setter
    def menu(self, value):
        self._menu = value
        self._update_menu()

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

    def _update_menu(self):
        """Updates the menu.

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


class MenuItem(object):
    """A single menu item.

    A menu item is immutable.

    It has a text and an activation callback. It is callable; when called,
    the activation callback is called.

    The :attr:`visible` attribute is provided to make menu creation easier; all
    menu items with this value set to  `False`` will be discarded when a
    :class:`Menu` is constructed.
    """
    def __init__(self, visible, text, on_activated, default=False):
        self._visible = visible
        self._text = text
        self.__name__ = text
        self._on_activated = on_activated
        self._default = default

    @property
    def visible(self):
        """Whether this menu item is visible.
        """
        return self._visible

    @property
    def text(self):
        """The menu item text.
        """
        return self._text

    @property
    def default(self):
        """Whether this is the default menu item.
        """
        return self._default

    def __call__(self, icon):
        return self._on_activated(icon)

    def __str__(self):
        return '    %s' % self.text


class Menu(object):
    """A description of a menu.

    A menu description is immutable.

    It is created with a sequence of either :class:`Menu.Item` instances,
    strings or tuples. If a non-:class:`Menu.Item` argument is passed, it is
    interpreted as a tuple to pass to the menu item contructor, with ``visible``
    set to ``True`` if it is a tuple, and a menu separator if it is the string
    ``'----'``.

    First, non-visible menu items are removed from the list, then any instances
    of :attr:`SEPARATOR` occurring at the head or tail of the item list are
    removed, and any consecutive separators are reduced to one.
    """
    #: A representation of a simple separator
    SEPARATOR = MenuItem(True, '- - - -', None)

    def __init__(self, *items):
        def cleaned(items):
            was_separator = False
            for i in items:
                if not i.visible:
                    continue

                if i is self.SEPARATOR:
                    if was_separator:
                        continue
                    was_separator = True
                else:
                    was_separator = False
                yield i

        def strip_head(items):
            return itertools.dropwhile(lambda i: i is self.SEPARATOR, items)

        def strip_tail(items):
            return reversed(list(strip_head(reversed(list(items)))))

        all_menuitems = [
            (
                i if isinstance(i, MenuItem)
                else self.SEPARATOR if i == '----'
                else MenuItem(True, *i))
            for i in items]
        try:
            self._activate = next(
                menuitem
                for menuitem in all_menuitems
                if menuitem.default)
        except StopIteration:
            self._activate = lambda _: None

        self._items = tuple(
            i if isinstance(i, MenuItem) else MenuItem(*i)
            for i in strip_tail(strip_head(cleaned(all_menuitems))))

    def __call__(self, icon):
        return self._activate(icon)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return 'Menu:\n' + '\n'.join(str(i) for i in self)
