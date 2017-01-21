Creating a *system tray icon*
-----------------------------

In order to create a *system tray icon*, the class ``pystray.Icon`` is used::

    import pystray

    icon = pystray.Icon('test name')


In order for the icon to be displayed, you must provide an icon. This icon must
be specified as a ``PIL.Image.Image``::

    from PIL import Image, ImageDraw

    def create_image():
        # Generate an image and draw a pattern
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)

        return image

    icon.icon = create_image()


To finally show you icon, run the following code::

    icon.run()


The call to ``pystray.Icon.run()`` is blocking, and it must be performed from
the main thread of the application. The reason for this is that the *system tray
icon* implementation for *OSX* will fail unless called from the main thread, and
it also requires the application runloop to be running. ``pystray.Icon.run()``
will start the runloop.

The ``run()`` method accepts an optional argument: ``setup``, a callable.

The ``setup`` funciton will be run in a separate thread once the *system tray
icon* is ready. The icon does not wait for it to complete, so you may put any
code that would follow the call to ``pystray.Icon.run()`` in it.

The call to ``pystray.Icon.run()`` will not complete until ``stop()`` is called.


Getting input from the *system tray icon*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to receive notifications about user interaction with the icon, a
popup menu can be added with the ``menu`` constructor argument.

This must be an instance of ``pystray.Menu``. Please see the reference for more
information about the format.

It will be displayed when the right-hand button has been pressed on the icon on
*Windows*, and when the icon has been clicked on other platforms. Menus are not
supported on *X*.

Menus also support a default item. On *Windows*, and *X*, this item will be
activated when the user clicks on the icon using the primary button. On other
platforms it will be activated if the menu contains no visible entries; it does
not have to be visible.

All properties of menu items, except for the callback, can be dynamically
calculated by supplying callables instead of values to the menu item
constructor. The properties are recalculated every time the icon is clicked or
any menu item is activated.

If the dynamic properties change because of an external event, you must ensure
that ``Icon.update_menu`` is called. This is required since not all supported
platforms allow for the menu to be generated when displayed.
