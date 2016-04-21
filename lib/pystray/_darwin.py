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

import io

import AppKit
import Foundation
import objc
import PIL

from . import _base


class Icon(_base.Icon):
    #: The selector for the button action
    _ACTION_SELECTOR = b'activate:sender'

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        #: The NSImage version of the icon
        self._icon_image = None

    def _show(self):
        self._assert_image()
        self._update_title()

        self._status_item.button().setHidden_(False)

    def _hide(self):
        self._status_item.button().setHidden_(True)

    def _update_icon(self):
        self._icon_image = None

        if self.visible:
            self._assert_image()

    def _update_title(self):
        self._status_item.button().setToolTip_(self.title)

    def _run(self):
        # Make sure there is an NSApplication instance
        self._app = AppKit.NSApplication.sharedApplication()

        # Make sure we have a delegate to handle the acttion events
        self._delegate = IconDelegate.alloc().init()
        self._delegate.icon = self

        self._status_bar = AppKit.NSStatusBar.systemStatusBar()
        self._status_item = self._status_bar.statusItemWithLength_(
            AppKit.NSVariableStatusItemLength)

        self._status_item.button().setTarget_(self._delegate)
        self._status_item.button().setAction_(self._ACTION_SELECTOR)
        self._status_item.button().setHidden_(True)

        # Notify the setup callback
        self._mark_ready()

        try:
            self._app.run()
        finally:
            self._status_bar.removeStatusItem_(self._status_item)

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
                'RGB',
                size)
            source.paste(self._icon.resize(
                size,
                PIL.Image.ANTIALIAS))

        # Convert the PIL image to an NSImage
        b = io.BytesIO()
        source.save(b, 'png')
        data = Foundation.NSData(b.getvalue())

        self._icon_image = AppKit.NSImage.alloc().initWithData_(data)
        self._status_item.button().setImage_(self._icon_image)


class IconDelegate(Foundation.NSObject):
    @objc.namedSelector(Icon._ACTION_SELECTOR)
    def activate(self, sender):
        self.icon.on_activate(self.icon)
