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

import functools
import io
import signal
import subprocess
import sys
import threading

import AppKit
import Foundation
import objc
import PIL
import  PyObjCTools.MachSignals

from . import _base


class _MainThreadCall(Foundation.NSObject):
    """Executes a Python call without letting exceptions cross into Cocoa.
    """
    def initWithPayload_(self, payload):
        self = objc.super(_MainThreadCall, self).init()
        if self is not None:
            self.payload = payload
            self.result = None
            self.exc_info = None
            self.completed = threading.Event()
        return self

    def invoke_(self, unused):
        function, args, kwargs = self.payload
        try:
            if not args[0]._stopped.is_set():
                self.result = function(*args, **kwargs)
        except BaseException:
            self.exc_info = sys.exc_info()
        finally:
            self.completed.set()


def _on_main_thread(function):
    """Runs an AppKit operation synchronously on the Cocoa main thread.
    """
    @functools.wraps(function)
    def inner(self, *args, **kwargs):
        if Foundation.NSThread.isMainThread():
            return function(self, *args, **kwargs)
        if self._stopped.is_set():
            return

        # The setup thread may not have an autorelease pool of its own.
        with objc.autorelease_pool():
            call = _MainThreadCall.alloc().initWithPayload_(
                (function, (self,) + args, kwargs))
            call.performSelectorOnMainThread_withObject_waitUntilDone_(
                'invoke:', None, False)
            # Do not strand the setup thread if stop() is called on the main
            # thread while it is waiting for an AppKit operation.
            while not call.completed.wait(0.1):
                if self._stopped.is_set():
                    return
            if call.exc_info is not None:
                _, exception, traceback = call.exc_info
                call.exc_info = None
                raise exception.with_traceback(traceback)
            return call.result
    return inner


class Icon(_base.Icon):
    #: The selector for the button action
    _ACTION_SELECTOR = b'activate:sender'

    #: The selector for the menu item actions
    _MENU_ITEM_SELECTOR = b'activateMenuItem:sender'

    # We support only a default action with an empty menu
    HAS_DEFAULT_ACTION = False

    # Mutually exclusive menu itema are not displayed distinctly
    HAS_MENU_RADIO = False

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        #: Set when the main loop can no longer service worker requests.
        self._stopped = threading.Event()

        #: The NSImage version of the icon
        self._icon_image = None

        #: The NSApplication managing this icon
        self._app = self._options['nsapplication'] \
            if 'nsapplication' in self._options \
            else AppKit.NSApplication.sharedApplication()

        #: The icon delegate
        self._delegate = IconDelegate.alloc().init()
        self._delegate.icon = self

        self._status_bar = AppKit.NSStatusBar.systemStatusBar()
        self._status_item = self._status_bar.statusItemWithLength_(
            AppKit.NSVariableStatusItemLength)

        self._status_item.button().setTarget_(self._delegate)
        self._status_item.button().setAction_(self._ACTION_SELECTOR)

    @_on_main_thread
    def _show(self):
        self._assert_image()
        self._update_title()

        self._status_item.button().setHidden_(False)

    @_on_main_thread
    def _hide(self):
        self._status_item.button().setHidden_(True)

    @_on_main_thread
    def _update_icon(self):
        self._icon_image = None

        if self.visible:
            self._assert_image()
            self._icon_valid = True

    @_on_main_thread
    def _update_title(self):
        self._status_item.button().setToolTip_(self.title)

    @_on_main_thread
    def _update_menu(self):
        callbacks = []
        nsmenu = self._create_menu(self.menu, callbacks)
        if nsmenu:
            self._status_item.setMenu_(nsmenu)
            self._menu_handle = (nsmenu, callbacks)
        else:
            self._status_item.setMenu_(None)
            self._menu_handle = None

    def _run(self):
        self._stopped.clear()
        # Notify the setup callback
        self._mark_ready()

        def sigint(*args):
            self._app.terminate_(None)
            if previous_sigint:
                previous_sigint(*args)

        # Make sure that we do not inhibit ctrl+c
        previous_sigint = PyObjCTools.MachSignals.signal(signal.SIGINT, sigint)

        try:
            self._app.run()
        except BaseException():
            self._queue.put(sys.exc_info())
        finally:
            self._stopped.set()
            if PyObjCTools.MachSignals.getsignal(signal.SIGINT) == sigint:
                PyObjCTools.MachSignals.signal(signal.SIGINT, previous_sigint)
            self._status_bar.removeStatusItem_(self._status_item)

    def _run_detached(self):
        self._stopped.clear()
        self._mark_ready()

    def _notify(self, message, title=None):
        subprocess.check_call([
            'osascript',
            '-e',
            'display notification "{}" with title "{}"'.format(
                message.replace('\\', '\\\\').replace('"', '\\"'),
                title.replace('\\', '\\\\').replace('"', '\\"'))])

    def _remove_notification(self):
        pass

    @_on_main_thread
    def _stop(self):
        self._app.stop_(self._app)

        # Post a dummy event; stop_ will only set a flag in NSApp, so it will
        # not terminate until an event has been processed
        event = getattr(
            AppKit.NSEvent,
            'otherEventWithType_'
            'location_'
            'modifierFlags_'
            'timestamp_'
            'windowNumber_'
            'context_'
            'subtype_'
            'data1_'
            'data2_')(
            AppKit.NSApplicationDefined,
            AppKit.NSPoint(0, 0),
            0,
            0.0,
            0,
            None,
            0,
            0,
            0)
        self._app.postEvent_atStart_(event, False)
        self._stopped.set()

    def _assert_image(self):
        """Asserts that the cached icon image exists.
        """
        thickness = self._status_bar.thickness()
        size = (int(thickness), int(thickness))
        if self._icon_image and self._icon_image.size() == size:
            return

        if self._icon.size == size:
            source = self._icon
        else:
            source = PIL.Image.new(
                'RGBA',
                size)
            source.paste(self._icon.resize(
                size,
                PIL.Image.LANCZOS))

        # Convert the PIL image to an NSImage
        b = io.BytesIO()
        source.save(b, 'png')
        data = Foundation.NSData(b.getvalue())

        self._icon_image = AppKit.NSImage.alloc().initWithData_(data)
        self._icon_image.setSize_(size)
        self._icon_image.setTemplate_(AppKit.YES)
        self._status_item.button().setImage_(self._icon_image)

    def _create_menu(self, descriptors, callbacks):
        """Creates a :class:`AppKit.NSMenu` from a :class:`pystray.Menu`
        instance.

        If :meth:`_run` has not yet been called, ``None`` is returned.

        :param descriptors: The menu descriptors. If this is falsy, ``None`` is
            returned.

        :param callbacks: A list to which a callback is appended for every menu
            item created. The menu item tags correspond to the items in this
            list.

        :return: a menu
        """
        if not descriptors:
            return None

        else:
            # Generate the menu
            nsmenu = AppKit.NSMenu.alloc().initWithTitle_(self.name)
            nsmenu.setAutoenablesItems_(False)
            for descriptor in descriptors:
                # Append the callback after creating the menu item to ensure
                # that the first item gets the tag 0
                nsmenu.addItem_(
                    self._create_menu_item(descriptor, callbacks))
                callbacks.append(self._handler(descriptor))

            return nsmenu

    def _create_menu_item(self, descriptor, callbacks):
        """Creates a :class:`AppKit.NSMenuItem` from a
        :class:`pystray.MenuItem` instance.

        :param descriptor: The menu item descriptor.

        :param callbacks: A list to which a callback is appended for every menu
            item created. The menu item tags correspond to the items in this
            list.

        :return: a :class:`AppKit.NSMenuItem`
        """
        if descriptor is _base.Menu.SEPARATOR:
            return AppKit.NSMenuItem.separatorItem()

        else:
            menu_item = AppKit.NSMenuItem.alloc() \
                .initWithTitle_action_keyEquivalent_(
                    descriptor.text, self._MENU_ITEM_SELECTOR, '')
            if descriptor.submenu:
                menu_item.setSubmenu_(self._create_menu(
                    descriptor.submenu, callbacks))
            else:
                menu_item.setAction_(self._MENU_ITEM_SELECTOR)
            menu_item.setTarget_(self._delegate)
            menu_item.setTag_(len(callbacks))
            if descriptor.default:
                menu_item.setAttributedTitle_(
                    Foundation.NSAttributedString.alloc()
                    .initWithString_attributes_(
                        descriptor.text,
                        Foundation.NSDictionary.alloc()
                        .initWithObjectsAndKeys_(
                            AppKit.NSFont.boldSystemFontOfSize_(
                                AppKit.NSFont.menuFontOfSize_(0)
                                .pointSize()),
                            AppKit.NSFontAttributeName)))
            if descriptor.checked is not None:
                menu_item.setState_(
                    AppKit.NSOnState if descriptor.checked
                    else AppKit.NSOffState)
            menu_item.setEnabled_(descriptor.enabled)
            return menu_item


class IconDelegate(Foundation.NSObject):
    @objc.namedSelector(Icon._ACTION_SELECTOR)
    def activate_button(self, sender):
        self.icon()

    @objc.namedSelector(Icon._MENU_ITEM_SELECTOR)
    def activate_menu_item(self, sender):
        nsmenu, callbacks = self.icon._menu_handle
        callbacks[sender.tag()](self.icon)
