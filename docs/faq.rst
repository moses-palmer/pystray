Frequently asked question
-------------------------

How do I use *pystray* in a *virtualenv* on *Linux*?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On *Linux*, runtime introspection data is required to use the *AppIndicator*
backend, and the *GTK* backend may not be fully functional without installing
desktop environment extensions. The *XOrg* backend will work, but it provides
limited functionality.

In order to use the *AppIndicator* backend, you may install the package
``PyGObject``. No wheel is provided, so the package must be built locally. On
*Debian* derivatives, such as *Ubuntu*, the following packages, in addition to
compilers and *pkg-config*, must be installed:

- ``libcairo-dev``
- ``libgirepository1.0-dev``

For *fedora* and similar distributions, please add the following packages to
enable *AppIndicator* support:

- ``libayatana-appindicator-gtk3``
- ``libayatana-appindicator-gtk3-devel``


I am trying to integrate with a framework, but ``run_detached`` does not work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``run_detached`` method is used to allow a different framework to drive the
main loop. This requires that the framework uses the same kind of mainloop.

On *Windows* and *macOS*, this will be the case if you use the platform GUI
toolkits. On *Linux*, the situation is a bit more complicated. Generally, the
*xorg* backend will work with any toolkit, as long as you run it in an *X*
session and not under *Wayland*. The *GTK* and *AppIndicator* backends will
work if your toolkit is based on *GObject*.

However, ``run_detached`` is strictly necessary only on *macOS*. For other
platforms, it is possible to just launch the icon mainloop in a thread::

    import pystray
    import threading
    import some_toolkit

    # Create the icon
    icon = pystray.Icon(
        'test name',
        icon=create_icon())

    # Run the icon mainloop in a separate thread
    threading.Thread(target=icon.run).start()

    # Run the toolkit mainlon in the main thread
    some_toolkit.mainloop()
