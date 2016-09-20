Creating a *system tray icon*
-----------------------------

In order to create a *system tray icon*, the class ``pystray.Icon`` is used::

    import pystray

    icon = pystray.Icon('test name')


In order for the icon to be displayed, you must provide an icon. This icon must
be specified as a ``PIL.Image.Image``::

    from PIL import Image, ImageDraw

    # Generate an image
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    icon.image = image


To ensure that your application runs on all platforms, you must then run the
following code to show the icon::

    def setup(icon):
        icon.visible = True

    icon.run(setup)


The call to ``pystray.Icon.run()`` is blocking, and it must be performed from
the main thread of the application. The reason for this is that the *system tray
icon* implementation for *OSX* must be run from the main thread, and it requires
the application runloop to be running. ``pystray.Icon.run()`` will start the
runloop.

The code in ``setup()`` will be run in a separate thread once the *system tray
icon* is ready. The icon does not wait for it to complete, so you may put any
code that would follow the call to ``pystray.Icon.run()`` in it.

The call to ``pystray.Icon.run()`` will not complete until ``stop()`` is called.


Getting input from the *system tray icon*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to receive notifications about user interaction with the icon, a
popup menu can be added with the ``menu`` constructor argument.

This should be an instance of ``pystray.Menu``, or a tuple that can be passed to
the ``pystray.Menu`` constructor. Please see the reference for more information
about the format.

It will be displayed when the right-hand button has been pressed on the icon on
*Windows* and *GTK+*, and when the icon has been clicked on *OSX*. Menus are not
supported on *X*.

Menus also support a default item. On *Windows*, *GTK+* and *X*, this item will
be activated when the user clicks on the icon using the primary button. On *OSX*
it will be activated if the menu contains no visible entries; it does not have
to be visible.

All properties of menu items, except for the callback, can be dynamically
calculated by supplying callables instead of values to the menu item
constructor. The properties are recalculated every time the icon is clicked or
any menu item is activated.

If the dynamic properties change because of an external event, you must ensure
that ``Icon.update_menu`` is called. This is required since not all supported
platforms allow for the menu to be generated when displayed.
