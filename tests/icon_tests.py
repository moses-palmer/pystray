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

import sys
import unittest

import pystray

from six.moves import queue
from six import reraise
from time import sleep

from pystray import Menu as menu, MenuItem as item

from . import action, confirm, icon, image, say, separator, true


#: The number of seconds to wait for interactive commands
TIMEOUT = 10


def test(icon):
    """A decorator to mark an inner function as the actual test code.

    The decorated function will be run in a separate thread as the ``setup``
    argument to :meth:`pystray.Icon.run`.

    This decorator actually runs the decorated method, and does not return
    anything.
    """
    def inner(f):
        q = queue.Queue()
        def setup(icon):
            try:
                f()
                q.put(True)
            except:
                q.put(sys.exc_info())
            finally:
                icon.visible = False
                icon.stop()
        icon.run(setup=setup)
        result = q.get()
        if result is not True:
            reraise(*result)

    return inner


def for_default_action(test):
    """Prevents a test from being run on implementations not supporting default
    action on click.

    :param test: The test.
    """
    if pystray.Icon.HAS_DEFAULT_ACTION:
        return test
    else:
        return lambda *a: None


def for_menu(test):
    """Prevents a test from being run on implementations not supporting a menu.

    :param test: The test.
    """
    if pystray.Icon.HAS_MENU:
        return test
    else:
        return lambda *a: None


def for_menu_radio(test):
    """Prevents a test from being run on implementations not supporting mutually
    exclusive menu item groups.

    :param test: The test.
    """
    if pystray.Icon.HAS_MENU_RADIO:
        return test
    else:
        return lambda *a: None


class IconTest(unittest.TestCase):
    def test_set_icon(self):
        """Tests that updating the icon works.
        """
        ico, colors1 = icon()
        original = ico.icon
        alternative, colors2 = image()

        @test(ico)
        def _():
            ico.visible = True
            for i in range(8):
                ico.icon = (alternative, original)[i % 2]
                sleep(0.5)

            confirm(
                self,
                'Did an alternating %s, and %s icon appear?', colors1, colors2)

    def test_set_icon_after_constructor(self):
        """Tests that updating the icon works.
        """
        ico, colors1 = icon(no_image=True)
        alternative, colors2 = image()

        @test(ico)
        def _():
            ico.icon = alternative
            ico.visible = True

            confirm(
                self,
                'Did an icon appear?')

    def test_set_icon_to_none(self):
        """Tests that setting the icon to None hides it.
        """
        ico, colors = icon()

        @test(ico)
        def _():
            ico.visible = True
            sleep(1.0)
            ico.icon = None
            self.assertFalse(ico.visible)

            confirm(
                self,
                'Did the %s icon disappear?', colors)

    def test_title(self):
        """Tests that initialising with a title works.
        """
        title = 'pystray test icon'
        ico, colors = icon(title=title)

        @test(ico)
        def _():
            ico.visible = True

            confirm(
                self,
                'Did an %s icon with the title "%s" appear?', colors, title)

    def test_title_set_hidden(self):
        """Tests that setting the title of a hidden icon works.
        """
        title = 'pystray test icon'
        ico, colors = icon(title='this is incorrect')

        @test(ico)
        def _():
            ico.title = title
            ico.visible = True

            confirm(
                self,
                'Did a %s icon with the title "%s" appear?', colors, title)

    def test_title_set_visible(self):
        """Tests that setting the title of a visible icon works.
        """
        title = 'pystray test icon'
        ico, colors = icon(title='this is incorrect')

        @test(ico)
        def _():
            ico.visible = True
            ico.title = title

            confirm(
                self,
                'Did a %s icon with the title "%s" appear?', colors, title)

    def test_visible(self):
        """Tests that the ``visible`` attribute reflects the visibility.
        """
        ico, colors = icon(title='this is incorrect')

        @test(ico)
        def _():
            self.assertFalse(ico.visible)
            ico.visible = True
            self.assertTrue(ico.visible)

    def test_visible_set(self):
        """Tests that showing a simple icon works.
        """
        ico, colors = icon()

        @test(ico)
        def _():
            ico.visible = True
            confirm(
                self,
                'Did a %s icon appear?', colors)

    def test_visible_set_no_icon(self):
        """Tests that setting the icon when none is set shows the icon.
        """
        ico = pystray.Icon('test')

        @test(ico)
        def _():
            try:
                with self.assertRaises(ValueError):
                    ico.visible = True

            finally:
                ico.visible = False

    def test_show_hide(self):
        """Tests that showing and hiding the icon works.
        """
        ico, colors = icon()

        @test(ico)
        def _():
            for i in range(4):
                ico.visible = True
                sleep(0.5)
                ico.visible = False
                sleep(0.5)

            confirm(
                self,
                'Did a flashing %s icon appear?', colors)

    @for_default_action
    def test_activate(self):
        """Tests that ``on_activate`` is correctly called.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        ico, colors = icon(menu=menu(
            action(on_activate),))

        @test(ico)
        def _():
            ico.visible = True

            say('Click the icon')
            q.get(timeout=TIMEOUT)

    def test_activate_with_default(self):
        """Tests that the default menu item is activated when activating icon.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        ico, colors = icon(menu=menu(
            item('Item 1', None),
            item('Default', on_activate, default=True)))

        @test(ico)
        def _():
            ico.visible = True

            say('Click the icon or select the default menu item')
            q.get(timeout=TIMEOUT)

    @for_menu
    def test_menu_construct(self):
        """Tests that the menu is constructed.
        """
        ico, colors = icon(menu=menu(
            item('Item 1', None),
            item('Item 2', None)))

        @test(ico)
        def _():
            ico.visible = True

            say('Expand the popup menu')
            confirm(
                self,
                'Was it\n%s?' % str(ico.menu))

    @for_menu
    def test_menu_activate(self):
        """Tests that the menu can be activated.
        """
        q = queue.Queue()

        def on_activate():
            q.put(True)

        ico, colors = icon(menu=(
            item('Item 1', on_activate),
            item('Item 2', None)))

        @test(ico)
        def _():
            ico.visible = True

            say('Click Item 1')
            q.get(timeout=TIMEOUT)

    @for_menu
    def test_menu_activate_method(self):
        """Tests that the menu can be activated and a method can be used.
        """
        q = queue.Queue()

        class C:
            def on_activate(self):
                q.put(True)

        c = C()
        ico, colors = icon(menu=(
            item('Item 1', c.on_activate),
            item('Item 2', None)))

        @test(ico)
        def _():
            ico.visible = True

            say('Click Item 1')
            q.get(timeout=TIMEOUT)

    @for_menu
    def test_menu_activate_submenu(self):
        """Tests that an item in a submenu can be activated.
        """
        q = queue.Queue()

        def on_activate():
            q.put(True)

        ico, colors = icon(menu=(
            item('Item 1', None),
            item('Submenu', menu(
                item('Item 2', None),
                item('Item 3', on_activate)))))

        @test(ico)
        def _():
            ico.visible = True

            say('Click Item 3 in the submenu')
            q.get(timeout=TIMEOUT)

    @for_default_action
    def test_menu_invisble(self):
        """Tests that a menu consisting of only empty items does not show.
        """
        q = queue.Queue()

        def on_activate():
            q.put(True)

        ico, colors = icon(menu=menu(
            item('Item1', None, visible=False),
            item('Item2', on_activate, default=True, visible=False)))

        @test(ico)
        def _():
            ico.visible = True

            say('Ensure that the menu does not show and then click the icon')
            q.get(timeout=TIMEOUT)

    @for_menu
    def test_menu_dynamic(self):
        """Tests that a dynamic menu works.
        """
        q = queue.Queue()
        q.ticks = 0

        def on_activate():
            q.put(True)
            q.ticks += 1

        ico, colors = icon(menu=menu(
            item('Item 1', on_activate),
            item('Item 2', None),
            item(lambda _:'Item ' + str(q.ticks + 3), None)))

        @test(ico)
        def _():
            ico.visible = True

            say('Click Item 1')
            q.get(timeout=TIMEOUT)

            say('Expand the popup menu')
            confirm(
                self,
                'Was it\n%s?' % str(ico.menu))

    @for_default_action
    @for_menu
    def test_menu_dynamic_show_hide(self):
        """Tests that a dynamic menu that is hidden works as expected.
        """
        q = queue.Queue()
        q.ticks = 0

        def on_activate():
            q.put(True)
            q.ticks += 1

        def visible(menu_item):
            return q.ticks % 2 == 0

        ico, colors = icon(menu=menu(
            item('Default', on_activate, default=True, visible=visible),
            item('Item 2', None, visible=visible)))

        @test(ico)
        def _():
            ico.visible = True

            say('Click the icon or select the default menu item')
            q.get(timeout=TIMEOUT)

            say('Ensure that the menu does not show and then click the icon')
            q.get(timeout=TIMEOUT)

            say('Expand the popup menu')
            confirm(
                self,
                'Was it\n%s?' % str(ico.menu))

    @for_menu_radio
    def test_menu_radio(self):
        """Tests that mutually exclusive items are displayed separately.
        """
        ico, colors = icon(menu=menu(
            item('Item 1', None, checked=true),
            item('Item 2', None, checked=true, radio=True)))

        @test(ico)
        def _():
            ico.visible = True

            say('Expand the popup menu')
            confirm(
                self,
                'Was <Item 2> displayed differently from <Item 1>?')

    @for_menu_radio
    def test_menu_enabled(self):
        """Tests that menu items can be disabled.
        """
        ico, colors = icon(menu=menu(
            item('Item 1', None, enabled=true),
            item('Item 2', None, enabled=False)))

        @test(ico)
        def _():
            ico.visible = True

            say('Expand the popup menu')
            confirm(
                self,
                'Was <Item 1> enabled and <Item 2> disabled?')

    if sys.platform == 'win32':

        def test_show_notification(self):
            """Tests that generation of a notification works.
            """
            ico, colors = icon()

            @test(ico)
            def _():
                ico.notify(title='Title: Test', message='This is a message!')

                confirm(
                    self,
                    'Did a notification appear?')

        def test_hide_notification(self):
            """Tests that a notification can be removed again.
            """
            ico, colors = icon()

            @test(ico)
            def _():
                ico.notify(title='Title: Test', message='This is a message!')
                sleep(5.0)
                ico.notify()

                confirm(
                    self,
                    'Was the notification removed?')
