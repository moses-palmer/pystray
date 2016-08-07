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

from ctypes import windll, wintypes


WM_CREATE = 0x0001
WM_NCCREATE = 0x0081
WM_LBUTTONDOWN = 0x0201
WM_USER = 0x400

WM_STOP = WM_USER + 10
WM_NOTIFY = WM_USER + 11


LR_DEFAULTSIZE = 0x00000040
LR_LOADFROMFILE = 0x00000010


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


PM_NOREMOVE = 0
COLOR_WINDOW = 5
HWND_MESSAGE = -3
IMAGE_ICON = 1


LPMSG = ctypes.POINTER(wintypes.MSG)

WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.HRESULT,
    wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class NOTIFYICONDATA(ctypes.Structure):
    class VERSION_OR_TIMEOUT(ctypes.Union):
        _fields_ = [
            ('uTimeout', wintypes.UINT),
            ('uVersion', wintypes.UINT)]

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

LPNOTIFYICONDATA = ctypes.POINTER(NOTIFYICONDATA)


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

LPWNDCLASSEX = ctypes.POINTER(WNDCLASSEX)


CreateWindowEx = windll.user32.CreateWindowExW
CreateWindowEx.argtypes = (
    wintypes.DWORD, wintypes.ATOM, wintypes.LPCWSTR, wintypes.DWORD,
    wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.HWND,
    wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID)
CreateWindowEx.restype = wintypes.HWND

DefWindowProc = windll.user32.DefWindowProcW
DefWindowProc.argtypes = (
    wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
DefWindowProc.restype = wintypes.DWORD

DestroyWindow = windll.user32.DestroyWindow
DestroyWindow.argtypes = (
    wintypes.HWND,)
DestroyWindow.restype = wintypes.BOOL

DispatchMessage = windll.user32.DispatchMessageW
DispatchMessage.argtypes = (
    LPMSG,)
DispatchMessage.restype = wintypes.DWORD

GetMessage = windll.user32.GetMessageW
GetMessage.argtypes = (
    LPMSG, wintypes.HWND, wintypes.UINT, wintypes.UINT)
GetMessage.restype = wintypes.BOOL

GetModuleHandle = windll.kernel32.GetModuleHandleW
GetModuleHandle.argtypes = (
    wintypes.LPCWSTR,)
GetModuleHandle.restype = wintypes.HMODULE

LoadImage = windll.user32.LoadImageW
LoadImage.argtypes = (
    wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, wintypes.INT,
    wintypes.INT, wintypes.UINT)
LoadImage.restype = wintypes.HANDLE

PeekMessage = windll.user32.PeekMessageW
PeekMessage.argtypes = (
    LPMSG, wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT)
PeekMessage.restype = wintypes.BOOL

PostMessage = windll.user32.PostMessageW
PostMessage.argtypes = (
    wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
PostMessage.restype = wintypes.BOOL

PostQuitMessage = windll.user32.PostQuitMessage
PostQuitMessage.argtypes = (
    wintypes.INT,)

RegisterClassEx = windll.user32.RegisterClassExW
RegisterClassEx.argtypes = (
    LPWNDCLASSEX,)
RegisterClassEx.restype = wintypes.ATOM

Shell_NotifyIcon = windll.shell32.Shell_NotifyIconW
Shell_NotifyIcon.argtypes = (
    wintypes.DWORD, LPNOTIFYICONDATA)
Shell_NotifyIcon.restype = wintypes.BOOL

TranslateMessage = windll.user32.TranslateMessage
TranslateMessage.argtypes = (
    LPMSG,)
TranslateMessage.restype = wintypes.BOOL

UnregisterClass = windll.user32.UnregisterClassW
UnregisterClass.argtypes = (
    wintypes.ATOM, wintypes.HINSTANCE)
UnregisterClass.restype = wintypes.BOOL
