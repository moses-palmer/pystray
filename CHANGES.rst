Release Notes
=============

v0.17.2 - Windows bug fixes
---------------------------
*  Actually release loaded icons on *Windows*. Thanks to *Bob1011941*!
*  Let mouse button release trigger menu and action on *Windows* as expected.
   Thanks to *Ennea*!


v0.17.1 - Corrected release notes
---------------------------------
*  Corrected attribution of *Windows* notification fix.


v0.17.0 - Various bug fixes
---------------------------
*  Corrected signalling in *GTK* backend. Thanks to *Simon Lindholm*!
*  Corrected hinding of notification message in *GTK backend*. Thanks to *Simon
   Lindholm*!
*  Corrected notification structure on *Windows*. Thanks to *flameiguana*!


v0.16.0 - Enable notifications
------------------------------
*  Added support for notifications. Thanks to *ralphwetzel* and *Chr0nicT*!
*  Added support for forcing the backend to use.


v0.15.0 - Allow methods as menu callbacks
-----------------------------------------
*  Allow passing a method as menu callback.
*  Ensure that the temporary file is removed when running under *AppIndicator*.
   Thanks to *superjamie*!


v0.14.4 - Allow setting icon after construction
-----------------------------------------------
*  Do not require setting ``icon`` twice when not passing the icon to the
   constructor.
*  Clarified documentation regarding name of menu argument.


v0.14.3 - Full license coverage
-------------------------------
*  Added license preamble to all source files. Thanks to *Björn Esser*!


v0.14.2 - Proper license files
------------------------------
*  Added proper license files. Thanks to *Björn Esser*!


v0.14.1 - Restore icon after *explorer.exe* crash
-------------------------------------------------
*  Restore the icon when *explorer exe* restarts after a crash. Thanks to
   *Michael Dubner*!


v0.14 - Disabled menu items
---------------------------
*  Added support for disabling menu items.


v0.13 - Corrections for X
-------------------------
*  Make sure to set window size hints on *X*. Thanks to *filonenko-mikhail*!


v0.12 - Simplified API
----------------------
*  Do not require use of ``setup`` to show icon.
*  Pass reference to menu item to action handler. If action handlers do not
   support this argument, they will be wrapped.
*  Updated documentation.


v0.11 - Radio buttons
---------------------
*  Added support for radio buttons.
*  Corrected transparent icons for *OSX*.


v0.10 - Changed Xlib backend library
------------------------------------
*  Changed *Xlib* library.
*  Corrected test with incorrect parameter.


v0.9 - Submenus
---------------
*  Added support for nested menus.


v0.8 - Platform independent API and checkable
---------------------------------------------
*  Added method to explicitly update menu to enable support for other platforms.
*  Added support for *AppIndicator* backend.
*  Re-added native clickability for *OSX*.
*  Added support for check boxes.


v0.7 - Dynamic menus
--------------------
*  Added support for dynamically generating menu item properties when a popup
   menu is displayed.
*  Display the default menu item distinctly.
*  Changed the menu item API slightly.
*  Corrected logging on Windows.


v0.6 - Simplified API
---------------------
*  Removed explicit default action parameter ``on_activate``.
*  Allow terminating the application with *ctrl+c* on *OSX*.
*  Added basic logging.


v0.5 - Menu support
-------------------
*  Added support for popup menus.
*  Corrected bug which prevented stopping the icon on *Windows*.
*  Corrected documentation.


v0.4 - GTK+ 3 support
---------------------
*  Added support for *GTK+* on *Linux*.


v0.3.5 - Corrected import errors
--------------------------------
*  Propagate import errors raised on Linux to help troubleshoot missing
   ``Xlib`` module. Thanks to Lance Kindle!
*  Properly declare ``six`` as a dependency.
*  Declare ``python3-xlib`` as dependency on *Linux* for *Python 3*.


v0.3.4 - Corrected Python 3 issues on Xorg
------------------------------------------
*  Make sure that ``pystray`` can be used on *Python 3* on *Xorg*.
*  Make sure the release making script runs on *Python 3*.


v0.3.3 - Corrected encoding issues
----------------------------------
*  Make sure building works even when default encoding is not *utf-8*.
*  Corrected issue with click selector on *OSX*.


v0.3.2 - Universal wheel
------------------------
*  Make sure to build a universal wheel for all python versions.


v0.3.1 - No-change packaging update
-----------------------------------
*  Do not package an old version of ``pynput``.


v0.3 - Proper Python 3 Support
------------------------------
*  Corrected Python 3 bugs.
*  Made ``Icon.run()`` mandatory on all platforms.


v0.2 - Initial Release
----------------------
*  Support for adding a system tray icon on *Linux*, *Mac OSX* and *Windows*.
