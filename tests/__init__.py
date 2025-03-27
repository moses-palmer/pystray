# coding=utf-8
# pystray
# Copyright (C) 2016-2025 Moses Palmér
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

from __future__ import print_function

import itertools

from PIL import Image, ImageDraw

import pystray

from pystray import MenuItem as item


COLORS = itertools.cycle((
    'black',
    'white',

    'red',
    'yellow',

    'blue',
    'red',

    'green',
    'white'))


def say(*args, **kwargs):
    """Prints a message, ensuring space between messages.
    """
    print('\n')
    print(*args, **kwargs)


def action(on_activate):
    """A convenience function to create a hidden default menu item.

    :param callable on_activate: The activation callback.
    """
    return item('Default', on_activate, default=True, visible=False)


def separator():
    """A wrapper around :attr:`pystray.Menu.SEPARATOR`.
    """
    return pystray.Menu.SEPARATOR


def icon(no_image=False, **kwargs):
    """Generates a systray icon with the specified colours.

    A systray icon created by this method will be automatically hidden
    when the current test finishes.

    :return: the tuple ``(icon, colors)``, where ``icon`` is a
        hidden systray icon, and ``colors`` is the ``colors`` return value
        of :meth:`image`.
    """
    img, colors = image()
    ico = pystray.Icon(
        'test',
        icon=img if not no_image else None,
        **kwargs)
    return ico, colors


def image(width=64, height=64):
    """Generates an icon image.

    :return: the tuple ``(image, colors)``, where  ``image`` is a
        *PIL* image and ``colors`` is a tuple containing the colours as
        *PIL* colour names, suitable for printing; the stringification of
        the tuple is also suitable for printing
    """
    class Colors(tuple):
        def __str__(self):
            return ' and '.join(self)

    colors = Colors((next_color(), next_color()))
    img = Image.new('RGB', (width, height), colors[0])
    dc = ImageDraw.Draw(img)

    dc.rectangle((width // 2, 0, width, height // 2), fill=colors[1])
    dc.rectangle((0, height // 2, width // 2, height), fill=colors[1])

    return img, colors

def next_color():
    """Returns the next colour to use.
    """
    return next(COLORS)


def confirm(self, statement, *fmt):
    """Asks the user to confirm a statement.

    :param self: An instance of a test suite.

    :param str statement: The statement to confirm.

    :raises AssertionError: if the user does not confirm
    """
    valid_responses = ('yes', 'y', 'no', 'n')
    accept_responses = valid_responses[:2]

    message = ('\n' + statement % fmt) + ' '
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


def true(*args):
    """Returns ``True``.
    """
    return True
