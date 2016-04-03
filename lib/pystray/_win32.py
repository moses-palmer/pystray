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

from ctypes import windll, wintypes
from six.moves import queue

from . import _base


class Icon(_base.Icon):
    _HWND_TO_ICON = {}

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._icon_handle = None
        self._hwnd = None

        # This is a mapping from win32 event codes to handlers used by the
        # mainloop
        self._message_handlers = {
            WM_STOP: self._on_stop,
            WM_NOTIFY: self._on_notify}

        self._queue = queue.Queue()

        # Create the message loop
        msg = wintypes.MSG()
        lpmsg = ctypes.byref(msg)
        PeekMessage(lpmsg, None, 0x0400, 0x0400, PM_NOREMOVE)

        self._atom = self._register_class()
        self._hwnd = self._create_window(self._atom)
        self._HWND_TO_ICON[self._hwnd] = self

    def __del__(self):
        if self._running:
            self._stop()
            if self._thread.ident != threading.current_thread().ident:
                self._thread.join()

    def _show(self):
        self._assert_icon_handle()
        self._message(
            NOTIFYICONDATA.NIM_ADD,
            NOTIFYICONDATA.NIF_MESSAGE | NOTIFYICONDATA.NIF_ICON |
            NOTIFYICONDATA.NIF_TIP,
            uCallbackMessage=WM_NOTIFY,
            hIcon=self._icon_handle,
            szTip=self.title)

    def _hide(self):
        self._message(
            NOTIFYICONDATA.NIM_DELETE,
            0)

    def _update_icon(self):
        self._icon_handle = None
        self._assert_icon_handle()
        self._message(
            NOTIFYICONDATA.NIM_MODIFY,
            NOTIFYICONDATA.NIF_ICON,
            hIcon=self._icon_handle)

    def _update_title(self):
        self._message(
            NOTIFYICONDATA.NIM_MODIFY,
            NOTIFYICONDATA.NIF_TIP,
            szTip=self.title)

    def _run(self):
        self._mark_ready()

        # Run the event loop
        self._thread = threading.current_thread()
        self._mainloop()

    def _stop(self):
        PostMessage(self._hwnd, WM_STOP, 0, 0)

    def _mainloop(self):
        """The body of the main loop thread.

        This method retrieves all events from *Windows* and makes sure to
        dispatch clicks.
        """
        # Pump messages
        try:
            while True:
                msg = wintypes.MSG()
                lpmsg = ctypes.byref(msg)
                while True:
                    r = GetMessage(lpmsg, None, 0, 0)
                    if not r:
                        break
                    elif r == -1:
                        break
                    else:
                        TranslateMessage(lpmsg)
                        DispatchMessage(lpmsg)

                # Make sure the icon is removed
                self._hide()

        except:
            # TODO: Report errors
            pass

        finally:
            try:
                self._hide()
                del self._HWND_TO_ICON[self._hwnd]
            except:
                pass

            DestroyWindow(self._hwnd)
            self._unregister_class(self._atom)

    def _on_stop(self, wparam, lparam):
        """Handles ``WM_STOP``.

        This method posts a quit message, causing the mainloop thread to
        terminate.
        """
        PostQuitMessage(0)

    def _on_notify(self, wparam, lparam):
        """Handles ``WM_NOTIFY``.

        This method calls the activate callback. It will only be called for
        left button clicks.
        """
        if lparam == WM_LBUTTONDOWN:
            self.on_activate(self)

    def _create_window(self, atom):
        """Creates the system tray icon window.

        :param atom: The window class atom.

        :return: a window
        """
        hwnd = CreateWindowEx(
            0,
            atom,
            None,
            0,
            0, 0, 0, 0,
            HWND_MESSAGE,
            None,
            GetModuleHandle(None),
            None)
        if not hwnd:
            raise ctypes.WinError(wintypes.get_last_error())
        else:
            return hwnd

    def _message(self, code, flags, **kwargs):
        """Sends a message the the systray icon.

        This method adds ``cbSize``, ``hWnd``, ``hId`` and ``uFlags`` to the
        message data.

        :param int message: The message to send. This should be one of the
            ``NIM_*`` constants.

        :param int flags: The value of ``NOTIFYICONDATA::uFlags``.

        :param kwargs: Data for the :class:`NOTIFYICONDATA` object.
        """
        r = Shell_NotifyIcon(code, ctypes.byref(NOTIFYICONDATA(
            cbSize=ctypes.sizeof(NOTIFYICONDATA),
            hWnd=self._hwnd,
            hID=id(self),
            uFlags=flags,
            **kwargs)))
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
                self._icon.save(f, format='ICO')
            hicon = LoadImage(
                None,
                wintypes.LPCWSTR(icon_path),
                IMAGE_ICON,
                0,
                0,
                LR_DEFAULTSIZE | LR_LOADFROMFILE)
            if not hicon:
                raise ctypes.WinError(wintypes.get_last_error())
            else:
                self._icon_handle = hicon

        finally:
            try:
                os.unlink(icon_path)
            except:
                pass

    def _register_class(self):
        """Registers the systray window class.

        :return: the class atom
        """
        window_class = WNDCLASSEX(
            cbSize=ctypes.sizeof(WNDCLASSEX),
            style=0,
            lpfnWndProc=_dispatcher,
            cbClsExtra=0,
            cbWndExtra=0,
            hInstance=GetModuleHandle(None),
            hIcon=None,
            hCursor=None,
            hbrBackground=COLOR_WINDOW + 1,
            lpszMenuName=None,
            lpszClassName='%s%dSystemTrayIcon' % (self.name, id(self)),
            hIconSm=None)
        atom = RegisterClassEx(ctypes.byref(window_class))
        if not atom:
            raise ctypes.WinError(wintypes.get_last_error())
        else:
            return atom

    def _unregister_class(self, atom):
        """Unregisters the systray window class.

        :param atom: The class atom returned by :meth:`_register_class`.
        """
        r = UnregisterClassEx(atom, GetModuleHandle(None))
        if not r:
            raise ctypes.WinError(wintypes.get_last_error())


WM_CREATE = 0x0001
WM_NCCREATE = 0x0081
WM_LBUTTONDOWN = 0x0201
WM_USER = 0x400
WM_STOP = WM_USER + 10
WM_NOTIFY = WM_USER + 11

HWND_MESSAGE = -3
PM_NOREMOVE = 0

COLOR_WINDOW = 5

IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040

NOTIFYICON_VERSION = 3

Shell_NotifyIcon = windll.shell32.Shell_NotifyIconW

GetModuleHandle = windll.kernel32.GetModuleHandleW

RegisterClassEx = windll.user32.RegisterClassExW
CreateWindowEx = windll.user32.CreateWindowExW
CreateWindowEx.argtypes = [
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.INT,
    wintypes.INT,
    wintypes.INT,
    wintypes.INT,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID]
CreateWindowEx.restype = wintypes.HWND
DestroyWindow = windll.user32.DestroyWindow
UnregisterClassEx = windll.user32.UnregisterClassW

LoadImage = windll.user32.LoadImageW

DispatchMessage = windll.user32.DispatchMessageW
GetMessage = windll.user32.GetMessageW
PeekMessage = windll.user32.PeekMessageW
PostMessage = windll.user32.PostMessageW
PostQuitMessage = windll.user32.PostQuitMessage
TranslateMessage = windll.user32.TranslateMessage


WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.HRESULT,
    wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASSEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.UINT),
        ('style', wintypes.UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', wintypes.INT),
        ('cbWndExtra', wintypes.INT),
        ('hInstance', wintypes.HANDLE),
        ('hIcon', wintypes.HICON),
        ('hCursor', wintypes.HANDLE),
        ('hbrBackground', wintypes.HBRUSH),
        ('lpszMenuName', wintypes.LPCWSTR),
        ('lpszClassName', wintypes.LPCWSTR),
        ('hIconSm', wintypes.HICON)]


@WNDPROC
def _dispatcher(hwnd, uMsg, wParam, lParam):
    try:
        return int(Icon._HWND_TO_ICON[hwnd]._message_handlers.get(
            uMsg, lambda w, l: 0)(wParam, lParam))

    except KeyError:
        # Icon._HWND_TO_ICON[hwnd] is not yet set; this message is sent during
        # window creation, so we assume it is WM_CREATE or WM_NCCREATE and
        # return TRUE
        return 1

    except:
        # TODO: Report
        return 0


class NOTIFYICONDATA(ctypes.Structure):
    class VERSION_OR_TIMEOUT(ctypes.Union):
        _fields_ = [
            ('uTimeout', wintypes.UINT),
            ('uVersion', wintypes.UINT)]

    NIF_MESSAGE = 0x00000001
    NIF_ICON = 0x00000002
    NIF_TIP = 0x00000004
    NIF_STATE = 0x00000008
    NIF_INFO = 0x00000010
    NIF_GUID = 0x00000020
    NIF_REALTIME = 0x00000040
    NIF_SHOWTIP = 0x00000080

    NIM_ADD = 0x00000000
    NIM_MODIFY = 0x00000001
    NIM_DELETE = 0x00000002
    NIM_SETFOCUS = 0x00000003
    NIM_SETVERSION = 0x00000004

    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT),
        ('uCallbackMessage', wintypes.UINT),
        ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 64),
        ('dwState', wintypes.DWORD),
        ('dwStateMask', wintypes.DWORD),
        ('szInfo', wintypes.WCHAR * 256),
        ('version_or_timeout', VERSION_OR_TIMEOUT),
        ('szInfoTitle', wintypes.WCHAR * 64),
        ('dwInfoFlags', wintypes.DWORD),
        ('guidItem', wintypes.LPVOID),
        ('hBalloonIcon', wintypes.HICON)]

    _anonymous_ = [
        'version_or_timeout']
