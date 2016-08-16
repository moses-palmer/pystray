import itertools
import sys
import unittest

import pystray

from PIL import Image, ImageDraw
from six.moves import input, queue
from six import reraise
from time import sleep


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


class IconTest(unittest.TestCase):
    def test_set_icon(self):
        """Tests that updating the icon works.
        """
        icon, colors1 = self.icon()
        original = icon.icon
        alternative, colors2 = self.image()

        @test(icon)
        def _():
            icon.visible = True
            for i in range(8):
                icon.icon = (alternative, original)[i % 2]
                sleep(0.5)

            self.confirm(
                'Did an alternating %s, and %s icon appear?', colors1, colors2)

    def test_set_icon_to_none(self):
        """Tests that setting the icon to None hides it.
        """
        icon, colors = self.icon()

        @test(icon)
        def _():
            icon.visible = True
            sleep(1.0)
            icon.icon = None
            self.assertFalse(icon.visible)

            self.confirm(
                'Did the %s icon disappear?', colors)

    def test_title(self):
        """Tests that initialising with a title works.
        """
        title = 'pystray test icon'
        icon, colors = self.icon(title=title)

        @test(icon)
        def _():
            icon.visible = True

            self.confirm(
                'Did an %s icon with the title "%s" appear?', colors, title)

    def test_title_set_hidden(self):
        """Tests that setting the title of a hidden icon works.
        """
        title = 'pystray test icon'
        icon, colors = self.icon(title='this is incorrect')

        @test(icon)
        def _():
            icon.title = title
            icon.visible = True

            self.confirm(
                'Did a %s icon with the title "%s" appear?', colors, title)

    def test_title_set_visible(self):
        """Tests that setting the title of a visible icon works.
        """
        title = 'pystray test icon'
        icon, colors = self.icon(title='this is incorrect')

        @test(icon)
        def _():
            icon.visible = True
            icon.title = title

            self.confirm(
                'Did a %s icon with the title "%s" appear?', colors, title)

    def test_visible(self):
        """Tests that the ``visible`` attribute reflects the visibility.
        """
        icon, colors = self.icon(title='this is incorrect')

        @test(icon)
        def _():
            self.assertFalse(icon.visible)
            icon.visible = True
            self.assertTrue(icon.visible)

    def test_visible_set(self):
        """Tests that showing a simple icon works.
        """
        icon, colors = self.icon()

        @test(icon)
        def _():
            icon.visible = True
            self.confirm(
                'Did a %s icon appear?', colors)

    def test_visible_set_no_icon(self):
        """Tests that setting the icon when none is set shows the icon.
        """
        icon = pystray.Icon('test')

        @test(icon)
        def _():
            try:
                with self.assertRaises(ValueError):
                    icon.visible = True

            finally:
                icon.visible = False

    def test_show_hide(self):
        """Tests that showing and hiding the icon works.
        """
        icon, colors = self.icon()

        @test(icon)
        def _():
            for i in range(4):
                icon.visible = True
                sleep(0.5)
                icon.visible = False
                sleep(0.5)

            self.confirm(
                'Did a flashing %s icon appear?', colors)

    def test_activate(self):
        """Tests that ``on_activate`` is correctly called.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        icon, colors = self.icon(on_activate=on_activate)

        @test(icon)
        def _():
            icon.visible = True

            print('Click the icon')
            q.get(timeout=5)

    def test_activate_with_default(self):
        """Tests that the default menu item is activated when activating icon.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        icon, colors = self.icon(menu=(
            ('Item 1', lambda _: None),
            ('Default', on_activate, True)))

        @test(icon)
        def _():
            icon.visible = True

            print('Click the icon or select the default menu item')
            q.get(timeout=5)

    def test_menu_construct(self):
        """Tests that the menu is constructed.
        """
        menu = (
            ('Item 1', lambda _: None),
            ('Item 2', lambda _: None))
        icon, colors = self.icon(menu=menu)

        @test(icon)
        def _():
            icon.visible = True

            print('Expand the popup menu')
            self.confirm(
                'Was it <%s>?' % str(pystray.Menu(*menu)))

    def test_menu_activate(self):
        """Tests that the menu can be activated.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        menu = (
            ('Item 1', on_activate),
            ('Item 2', lambda _: None))
        icon, colors = self.icon(menu=menu)

        @test(icon)
        def _():
            icon.visible = True

            print('Click Item 1')
            q.get(timeout=5)

    def test_menu_invisble(self):
        """Tests that a menu consisting of only empty items does not show.
        """
        q = queue.Queue()

        def on_activate(icon):
            q.put(True)

        menu = (
            ('Item 1', on_activate),
            ('Item 2', lambda _: None))
        icon, colors = self.icon(menu=(
            pystray.MenuItem(False, 'Item1', lambda _: None),
            pystray.MenuItem(False, 'Item1', on_activate, default=True)))

        @test(icon)
        def _():
            icon.visible = True

            print('Ensure that the menu does not show and then click the icon')
            q.get(timeout=5)

    def icon(self, **kwargs):
        """Generates a systray icon with the specified colours.

        A systray icon created by this method will be automatically hidden
        when the current test finishes.

        :return: the tuple ``(icon, colors)``, where ``icon`` is a
            hidden systray icon, and ``colors`` is the ``colors`` return value
            of :meth:`image`.
        """
        image, colors = self.image()
        icon = pystray.Icon(
            'test',
            icon=image,
            **kwargs)
        return icon, colors

    def image(self, width=64, height=64):
        """Generates an icon image.

        :return: the tuple ``(image, colors)``, where  ``image`` is a
            *PIL* image and ``colors`` is a tuple containing the colours as
            *PIL* colour names, suitable for printing; the stringification of
            the tuple is also suitable for printing
        """
        class Colors(tuple):
            def __str__(self):
                return ' and '.join(self)

        colors = Colors((self.next_color(), self.next_color()))
        image = Image.new('RGB', (width, height), colors[0])
        dc = ImageDraw.Draw(image)

        dc.rectangle((width // 2, 0, width, height // 2), fill=colors[1])
        dc.rectangle((0, height // 2, width // 2, height), fill=colors[1])

        return image, colors

    def next_color(self):
        """Returns the next colour to use.
        """
        return next(self._colors)

    @classmethod
    def setUpClass(cls):
        cls._colors = itertools.cycle((
            'black',
            'white',

            'red',
            'yellow',

            'blue',
            'red',

            'green',
            'white'))

    def confirm(self, statement, *fmt):
        """Asks the user to confirm a statement.

        :param str statement: The statement to confirm.

        :raises AssertionError: if the user does not confirm
        """
        valid_responses = ('yes', 'y', 'no', 'n')
        accept_responses = valid_responses[:2]

        message = (statement % fmt) + ' '
        while True:
            response = input(message)
            if response.lower() in valid_responses:
                self.assertIn(
                    response.lower(), accept_responses,
                    'User declined statement "%s"' % message)
                return
            else:
                print(
                    'Please respond %s' % ', '.join(
                        '"%s"' % r for r in valid_responses))
