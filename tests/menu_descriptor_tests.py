# coding=utf-8
# pystray
# Copyright (C) 2016-2022 Moses Palmér
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

import unittest

import pystray

from pystray import Menu as menu
from pystray import MenuItem as item

from . import separator, true


class MenuDescriptorTests(unittest.TestCase):
    def test_item_name(self):
        """Tests that the text is set correctly.
        """
        self.assertEqual(
            'Test entry',
            item('Test entry', None).text)

    def test_item_call(self):
        """Tests that calling a menu item works as expected.
        """
        data = []
        item('', lambda: data.append(True))(None)
        self.assertEqual(
            [True],
            data)

    def test_item_call_various_args(self):
        """Tests that calling a menu item works as expected.
        """
        item('', lambda: None)(None)
        item('', lambda a: a)(None)
        item('', lambda a, b: (a, b))(None)
        with self.assertRaises(ValueError):
            item('', lambda a, b, c: (a, b, ))

    def test_menu_construct(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '''
    Test entry one
    Test entry two
    Test entry three
    Test entry four''',
        '\n' + str(menu(
            item('Test entry one', None),
            item('Test entry two', None),
            item('Test entry three', None),
            item('Test entry four', None))))

    def test_menu_construct_from_generator(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '''
    Test entry 1
    Test entry 2
    Test entry 3
    Test entry 4''',
        '\n' + str(menu(lambda: (
            item('Test entry %d' % (i + 1), None)
            for i in range(4)))))

    def test_menu_construct_from_none(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '',
            '\n' + str(menu(None)))

    def test_menu_construct_with_submenu(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '''
    Test entry 1
    Test entry 2 =>
        Test entry 3
        Test entry 4
    Test entry 5''',
        '\n' + str(menu(
                item('Test entry 1', None),
                item('Test entry 2', menu(
                    item('Test entry 3', None),
                    item('Test entry 4', None))),
                item('Test entry 5', None))))

    def test_menu_separator(self):
        """Tests menu construction with separators.
        """
        # Separators at the head and tail are ignored
        self.assertEqual(
            '''
    Test entry one
    - - - -
    Test entry two''',
        '\n' + str(menu(
            separator(),
            separator(),
            item('Test entry one', None),
            separator(),
            item('Test entry hidden', None, visible=False),
            separator(),
            item('Test entry two', None),
            separator(),
            separator())))

    def test_menu_default_none(self):
        """Tests that an invalid number of default menu items fails.
        """
        self.assertIsNone(
            menu(
                item('one', true, default=False),
                item('two', true, default=False))(None))

    def test_menu_default_callable(self):
        """Tests that the default menu item is activated when calling the menu.
        """
        self.assertEqual(
            'test result',
            menu(
                item('one', lambda: 'test result', default=True))(None))

    def test_menu_visible_submenu(self):
        """Tests that  ``visible`` is correctly set when a submenu is set.
        """
        self.assertTrue(
            item('Test', menu(
                item('Item', None)), visible=True).visible)
        self.assertFalse(
            item('Test', menu(
                item('Item', None)), visible=False).visible)
        self.assertFalse(
            item('Test', menu(
                item('Item', None, visible=False)), visible=True).visible)

    def test_menu_enabled_default(self):
        """Tests that a menu item is enabled by default.
        """
        self.assertTrue(
            item(
                'one', lambda: 'test result').enabled)

    def test_menu_enabled_callable(self):
        """Tests that the enabled state can be set.
        """
        self.assertFalse(
            item(
                'one', lambda: 'test result', enabled=False).enabled)

    def test_menu_checked_none(self):
        """Tests that not providing a value for ``default`` works.
        """
        self.assertFalse(
            item('Test', None).checked)

    def test_menu_checked_non_callable(self):
        """Tests that not passing a callable as checked fails.
        """
        with self.assertRaises(ValueError):
            item('Test', None, checked=False)

    def test_menu_checked_non_callable(self):
        """Tests that not providing a value for ``default`` works.
        """
        self.assertTrue(
            item('Test', None, checked=true).checked)

    def test_menu_radio_uncheckable(self):
        """Tests that not providing a value for ``checked`` for uncheckable
        items works.
        """
        self.assertFalse(
            item('Test', None).radio)
        self.assertFalse(
            item('Test', None, radio=False).radio)
        self.assertFalse(
            item('Test', None, radio=True).radio)

    def test_menu_radio_checkable(self):
        """Tests that providing a value for ``checked`` for checkable items
        works.
        """
        self.assertFalse(
            item('Test', None, checked=true).radio)
        self.assertTrue(
            item('Test', None, checked=true, radio=True).radio)
        self.assertTrue(
            item('Test', None, checked=true, radio=true).radio)
