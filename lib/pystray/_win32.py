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

import ctypes
import os
import six
import sys
import threading
import tempfile

from ctypes import wintypes
from six.moves import queue

from ._util import win32
from . import _base


class Icon(_base.Icon):
    _HWND_TO_ICON = {}

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._icon_handle = None
        self._hwnd = None
        self._menu_hwnd = None
        self._hmenu = None

        # This is a mapping from win32 event codes to handlers used by the
        # mainloop
        self._message_handlers = {
            win32.WM_STOP: self._on_stop,
            win32.WM_NOTIFY: self._on_notify}

        self._queue = queue.Queue()

        # Create the message loop
        msg = wintypes.MSG()
        lpmsg = ctypes.byref(msg)
        win32.PeekMessage(
            lpmsg, None, win32.WM_USER, win32.WM_USER, win32.PM_NOREMOVE)

        self._atom = self._register_class()
        self._hwnd = self._create_window(self._atom)
        self._menu_hwnd = self._create_window(self._atom)
        self._hmenu = win32.CreatePopupMenu()
        self._HWND_TO_ICON[self._hwnd] = self

        if self.menu:
            self._update_menu()

    def __del__(self):
        if self._running:
            self._stop()
            if self._thread.ident != threading.current_thread().ident:
                self._thread.join()

    def _show(self):
        self._assert_icon_handle()
        self._message(
            win32.NIM_ADD,
            win32.NIF_MESSAGE | win32.NIF_ICON | win32.NIF_TIP,
            uCallbackMessage=win32.WM_NOTIFY,
            hIcon=self._icon_handle,
            szTip=self.title)

    def _hide(self):
        self._message(
            win32.NIM_DELETE,
            0)

    def _update_icon(self):
        self._icon_handle = None
        self._assert_icon_handle()
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_ICON,
            hIcon=self._icon_handle)

    def _update_title(self):
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_TIP,
            szTip=self.title)

    def _update_menu(self):
        # Just clear the menu if none is set
        win32.DestroyMenu(self._hmenu)
        self._hmenu = win32.CreatePopupMenu()
        if not self.menu:
            return

        # Generate the menu
        for i, descriptor in enumerate(self.menu):
            # Use the index plus one as menu item identifier; we cannot use the
            # index directly, since TrackPopupMenuEx will return 0 if no item
            # was selected
            menu_item = self._create_menu_item(descriptor, i + 1)
            if not win32.InsertMenuItem(
                    self._hmenu, i, True, ctypes.byref(menu_item)):
                raise ctypes.WinError(wintypes.get_last_error())

    def _run(self):
        self._mark_ready()

        # Run the event loop
        self._thread = threading.current_thread()
        self._mainloop()

    def _stop(self):
        win32.PostMessage(self._hwnd, win32.WM_STOP, 0, 0)

    def _mainloop(self):
        """The body of the main loop thread.

        This method retrieves all events from *Windows* and makes sure to
        dispatch clicks.
        """
        # Pump messages
        try:
            msg = wintypes.MSG()
            lpmsg = ctypes.byref(msg)
            while True:
                r = win32.GetMessage(lpmsg, None, 0, 0)
                if not r:
                    break
                elif r == -1:
                    break
                else:
                    win32.TranslateMessage(lpmsg)
                    win32.DispatchMessage(lpmsg)

            # Make sure the icon is removed
            self._hide()

        except:
            self._log.error(
                'An error occurred in the main loop', exc_info=True)

        finally:
            try:
                self._hide()
                del self._HWND_TO_ICON[self._hwnd]
            except:
                self._log.error(
                    'An error occurred after the main loop', exc_info=True)

            win32.DestroyWindow(self._hwnd)
            win32.DestroyWindow(self._menu_hwnd)
            win32.DestroyMenu(self._hmenu)
            self._unregister_class(self._atom)

    def _on_stop(self, wparam, lparam):
        """Handles ``WM_STOP``.

        This method posts a quit message, causing the mainloop thread to
        terminate.
        """
        win32.PostQuitMessage(0)

    def _on_notify(self, wparam, lparam):
        """Handles ``WM_NOTIFY``.

        If this is a left button click, this icon will be activated. If a menu
        is registered and this is a right button click, the popup menu will be
        displayed.
        """
        if lparam == win32.WM_LBUTTONDOWN:
            self()

        elif self.menu and lparam == win32.WM_RBUTTONDOWN:
            # TrackPopupMenuEx does not behave unless our systray window is the
            # foreground window
            win32.SetForegroundWindow(self._hwnd)

            # Get the cursor position to determine where to display the menu
            point = wintypes.POINT()
            if not win32.GetCursorPos(ctypes.byref(point)):
                self._log.error('Failed to get cursor position')
                return

            # Display the menu and get the menu item identifier; the identifier
            # is the menu item index plus one
            identifier = win32.TrackPopupMenuEx(
                self._hmenu,
                win32.TPM_RIGHTALIGN | win32.TPM_BOTTOMALIGN
                | win32.TPM_RETURNCMD,
                point.x,
                point.y,
                self._menu_hwnd,
                None)
            if identifier:
                self.menu[identifier - 1](self)
            else:
                self._log.error('Unknown menu item identifier: %d' % identifier)

    def _create_window(self, atom):
        """Creates the system tray icon window.

        :param atom: The window class atom.

        :return: a window
        """
        hwnd = win32.CreateWindowEx(
            0,
            atom,
            None,
            0,
            0, 0, 0, 0,
            win32.HWND_MESSAGE,
            None,
            win32.GetModuleHandle(None),
            None)
        if not hwnd:
            raise ctypes.WinError(wintypes.get_last_error())
        else:
            return hwnd

    def _create_menu_item(self, descriptor, identifier):
        """Creates a :class:`pystray._util.win32.MENUITEMINFO` from a
        :class:`pystray.MenuItem` instance.

        :param descriptor: The menu item descriptor.

        :param int identifier: The menu item identifier

        :return: a :class:`pystray._util.win32.MENUITEMINFO`
        """
        if descriptor is _base.Menu.SEPARATOR:
            return win32.MENUITEMINFO(
                cbSize=ctypes.sizeof(win32.MENUITEMINFO),
                fMask=win32.MIIM_FTYPE,
                fType=win32.MFT_SEPARATOR)

        else:
            return win32.MENUITEMINFO(
                cbSize=ctypes.sizeof(win32.MENUITEMINFO),
                fMask=win32.MIIM_STRING | win32.MIIM_ID,
                wID=identifier,
                dwTypeData=descriptor.text)

    def _message(self, code, flags, **kwargs):
        """Sends a message the the systray icon.

        This method adds ``cbSize``, ``hWnd``, ``hId`` and ``uFlags`` to the
        message data.

        :param int message: The message to send. This should be one of the
            ``NIM_*`` constants.

        :param int flags: The value of ``NOTIFYICONDATA::uFlags``.

        :param kwargs: Data for the :class:`NOTIFYICONDATA` object.
        """
        r = win32.Shell_NotifyIcon(code, win32.NOTIFYICONDATA(
            cbSize=ctypes.sizeof(win32.NOTIFYICONDATA),
            hWnd=self._hwnd,
            hID=id(self),
            uFlags=flags,
            **kwargs))
        if not r:
            raise ctypes.WinError(wintypes.get_last_error())

    def _assert_icon_handle(self):
        """Asserts that the cached icon handle exists.
        """
        if self._icon_handle:
            return

        fd, icon_path = tempfile.mkstemp('.ico')
        try:
            with os.fdopen(fd, 'wb') as f:
                self.icon.save(f, format='ICO')
            hicon = win32.LoadImage(
                None,
                icon_path,
                win32.IMAGE_ICON,
                0,
                0,
                win32.LR_DEFAULTSIZE | win32.LR_LOADFROMFILE)
            if not hicon:
                raise ctypes.WinError(wintypes.get_last_error())
            else:
                self._icon_handle = hicon

        finally:
            try:
                os.unlink(icon_path)
            except:
                self._log.error(
                    'Failed to remove temporary icon', exc_info=True)

    def _register_class(self):
        """Registers the systray window class.

        :return: the class atom
        """
        window_class = win32.WNDCLASSEX(
            cbSize=ctypes.sizeof(win32.WNDCLASSEX),
            style=0,
            lpfnWndProc=_dispatcher,
            cbClsExtra=0,
            cbWndExtra=0,
            hInstance=win32.GetModuleHandle(None),
            hIcon=None,
            hCursor=None,
            hbrBackground=win32.COLOR_WINDOW + 1,
            lpszMenuName=None,
            lpszClassName='%s%dSystemTrayIcon' % (self.name, id(self)),
            hIconSm=None)
        atom = win32.RegisterClassEx(window_class)
        if not atom:
            raise ctypes.WinError(wintypes.get_last_error())
        else:
            return atom

    def _unregister_class(self, atom):
        """Unregisters the systray window class.

        :param atom: The class atom returned by :meth:`_register_class`.
        """
        r = win32.UnregisterClass(atom, win32.GetModuleHandle(None))
        if not r:
            raise ctypes.WinError(wintypes.get_last_error())


@win32.WNDPROC
def _dispatcher(hwnd, uMsg, wParam, lParam):
    """The function used as window procedure for the systray window.
    """
    # These messages are sent before Icon._HWND_TO_ICON[hwnd] has been set, so
    # we handle them explicitly
    if uMsg == win32.WM_NCCREATE:
        return True
    if uMsg == win32.WM_CREATE:
        return 0

    try:
        icon = Icon._HWND_TO_ICON[hwnd]
    except KeyError:
        return win32.DefWindowProc(hwnd, uMsg, wParam, lParam)

    try:
        return int(icon._message_handlers.get(
            uMsg, lambda w, l: 0)(wParam, lParam))

    except:
        icon._log.error(
            'An error occurred when calling message handler', exc_info=True)
        return 0
