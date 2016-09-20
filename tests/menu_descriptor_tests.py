import unittest

import pystray

from pystray import Menu as menu
from pystray import MenuItem as item


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
        item('', lambda _: data.append(True))(None)
        self.assertEqual(
            [True],
            data)

    def test_menu_construct(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '''Menu:
    Test entry one
    Test entry two
    Test entry three
    Test entry four''',
        str(menu(
            item('Test entry one', None),
            item('Test entry two', None),
            item('Test entry three', None),
            item('Test entry four', None))))

    def test_menu_construct_from_generator(self):
        """Tests menu construction.
        """
        self.assertEqual(
            '''Menu:
    Test entry 1
    Test entry 2
    Test entry 3
    Test entry 4''',
        str(menu(lambda: (
            item('Test entry %d' % (i + 1), None)
            for i in range(4)))))

    def test_menu_separator(self):
        """Tests menu construction with separators.
        """
        # Separators at the head and tail are ignored
        self.assertEqual(
            '''Menu:
    Test entry one
    - - - -
    Test entry two''',
        str(menu(
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
                item('one', lambda _: True, default=False),
                item('two', lambda _: True, default=False))(None))

    def test_menu_default_callable(self):
        """Tests that the default menu item is activated when calling the menu.
        """
        self.assertEqual(
            'test result',
            menu(
                item('one', lambda _: 'test result', default=True))(None))


def separator():
    """A wrapper around :attr:`pystray.Menu.SEPARATOR`.
    """
    return pystray.Menu.SEPARATOR
