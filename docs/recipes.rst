.. _recipes:

=======
Recipes
=======


Auto Bridge
===========

This recipe (and several others in this chapter) was shamelessly stolen from
`Martin O'Hanlon's excellent site`_ which includes lots of recipes (although at
the time of writing they're all for the mcpi API).

The script tracks the position and likely future position of the player as
they walk through the world. If the script detects the player is about to walk
onto air it changes the block to diamond:

.. literalinclude:: recipe_bridge.py

Note that the script starts by initializing the connection with the
``ignore_errors=True`` parameter. This causes the picraft library to act like
the mcpi library: errors in "set" calls are ignored, but the library reacts
faster because of this. This is necessary in a script like this where rapid
reaction to player behaviour is required.


Minecraft TV
============

If you've got a Raspberry Pi camera module, you can build a TV to view a live
feed from the camera in the Minecraft world. Firstly we need to construct a
class which will accept JPEGs from the camera's MJPEG stream, and render them
as blocks in the Minecraft world. Then we need a class to construct the TV
model itself and enable interaction with it:

.. literalinclude:: recipe_tv.py

.. _Martin O'Hanlon's excellent site: http://www.stuffaboutcode.com/
