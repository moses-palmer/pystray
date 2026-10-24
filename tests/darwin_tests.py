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

import sys
import threading
import unittest

from PIL import Image

if sys.platform == 'darwin':
    import Foundation
    from PyObjCTools import AppHelper
    from pystray import Menu, MenuItem
    from pystray._darwin import Icon, _on_main_thread


@unittest.skipUnless(sys.platform == 'darwin', 'Requires Cocoa')
class DarwinThreadTests(unittest.TestCase):
    def run_worker(self, callback):
        """Run a worker while the real Cocoa event loop services its calls.
        """
        icon = Icon('thread-test', Image.new('RGBA', (22, 22), 'black'))
        errors = []

        def setup(icon):
            try:
                callback(icon)
            except BaseException:
                errors.append(sys.exc_info())
            finally:
                icon.visible = False
                icon.stop()

        icon.run(setup=setup)
        if errors:
            _, exception, traceback = errors[0]
            raise exception.with_traceback(traceback)

    def test_main_thread_result(self):
        @_on_main_thread
        def operation(icon, value, offset=0):
            self.assertTrue(Foundation.NSThread.isMainThread())
            return value + offset

        self.assertEqual(operation(Icon('result-test'), 20, offset=22), 42)

    def test_main_thread_exception(self):
        @_on_main_thread
        def operation(icon):
            raise ValueError('main-thread failure')

        with self.assertRaisesRegex(ValueError, 'main-thread failure'):
            operation(Icon('exception-test'))

    def test_worker_result_and_nested_call(self):
        @_on_main_thread
        def nested(icon, value):
            self.assertTrue(Foundation.NSThread.isMainThread())
            return value

        @_on_main_thread
        def operation(icon, value, offset=0):
            return nested(icon, value + offset)

        def worker(icon):
            self.assertFalse(Foundation.NSThread.isMainThread())
            self.assertEqual(operation(icon, 20, offset=22), 42)

        self.run_worker(worker)

    def test_worker_exception(self):
        @_on_main_thread
        def operation(icon):
            raise ValueError('worker failure')

        def worker(icon):
            with self.assertRaisesRegex(ValueError, 'worker failure'):
                operation(icon)
            # A failed operation must not break subsequent dispatches.
            self.assertTrue(_on_main_thread(
                lambda icon: Foundation.NSThread.isMainThread())(icon))

        self.run_worker(worker)

    def test_worker_appkit_updates(self):
        @_on_main_thread
        def check(icon, title, menu_title):
            self.assertEqual(icon._status_item.button().toolTip(), title)
            self.assertIsNotNone(icon._status_item.button().image())
            self.assertEqual(
                icon._status_item.menu().itemAtIndex_(0).title(), menu_title)

        def label(item):
            self.assertTrue(Foundation.NSThread.isMainThread())
            return 'Updated'

        def worker(icon):
            icon.visible = True
            icon.title = 'Updated title'
            icon.icon = Image.new('RGBA', (22, 22), 'red')
            icon.menu = Menu(MenuItem(label, None))
            for _ in range(10):
                icon.update_menu()
            check(icon, 'Updated title', 'Updated')
            icon.menu = None
            self.assertIsNone(_on_main_thread(
                lambda icon: icon._status_item.menu())(icon))
            icon.visible = False
            icon.visible = True

        self.run_worker(worker)

    def test_default_setup(self):
        # Icon.run() itself shows the icon from its default setup thread.
        icon = Icon('default-setup', Image.new('RGBA', (22, 22), 'black'))
        observations = []

        def check():
            observations.append(icon._status_item.button().image() is not None)
            icon.visible = False
            icon.stop()

        # Queue the check behind the synchronous show operation. The default
        # setup thread returns after visible=True has completed.
        def wait_for_setup():
            icon._setup_thread.join()
            AppHelper.callAfter(check)

        AppHelper.callAfter(lambda: threading.Thread(
            target=wait_for_setup, daemon=True).start())
        icon.run()
        self.assertEqual(observations, [True])

    def test_stop_releases_waiting_setup(self):
        icon = Icon('shutdown-test')
        # The main thread stops before servicing the setup thread's request.
        icon.SETUP_THREAD_TIMEOUT = 1
        finished = threading.Event()
        errors = []

        def setup(icon):
            AppHelper.callAfter(icon.stop)
            try:
                icon.menu = Menu(MenuItem('Pending', None))
                icon.title = 'After shutdown'
            except BaseException:
                errors.append(sys.exc_info())
            finally:
                finished.set()

        icon.run(setup=setup)
        self.assertTrue(finished.wait(1), 'Setup remained blocked after stop')
        self.assertEqual(errors, [])

    def test_worker_after_stop(self):
        icons = []
        self.run_worker(lambda icon: icons.append(icon))
        finished = threading.Event()

        def worker():
            icons[0].menu = Menu(MenuItem('After stop', None))
            finished.set()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        self.assertTrue(finished.wait(1), 'Update waited for a stopped main loop')
        thread.join(1)
