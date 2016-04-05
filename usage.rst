Creating a *system tray icon*
-----------------------------

In order to create a *system tray icon*, the class ``pystray.Icon`` is used::

    import pystray

    icon = pystray.Icon('test name')


In order for the icon to be displayed, we must provide an icon. This icon must
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

``pystray.Icon.run()`` will not complete until ``~pystray.Icon.stop()`` is
called.
