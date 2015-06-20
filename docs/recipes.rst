.. _recipes:

=======
Recipes
=======


Auto Bridge
===========

This recipe (and several others in this chapter) was shamelessly stolen from
`Martin O'Hanlon's excellent site`_ which includes lots of recipes (although at
the time of writing they're all for the mcpi API). In this case the original
script can be found in Martin's `auto-bridge project`_.

The script tracks the position and likely future position of the player as
they walk through the world. If the script detects the player is about to walk
onto air it changes the block to diamond:

.. literalinclude:: recipe_bridge.py

Note that the script starts by initializing the connection with the
``ignore_errors=True`` parameter. This causes the picraft library to act like
the mcpi library: errors in "set" calls are ignored, but the library reacts
faster because of this. This is necessary in a script like this where rapid
reaction to player behaviour is required.


Shapes
======

This recipe demonstrates drawing shapes with blocks in the Minecraft world. The
picraft library includes a couple of rudimentary routines for calculating the
points necessary for drawing lines:

* :func:`~picraft.vector.line` which can be used to calculate the positions
  along a single line

* :func:`~picraft.vector.lines` which calculates the positions along a series
  of lines

Here we will attempt to construct a script which draws each regular polygon
from an equilateral triangle up to a regular octagon. First we start by
defining a function which will generate the points of a regular polygon. This
is relatively simple: the interior angles of a polygon always add up to 180
degrees so the angle to turn each time is 180 divided by the number of sides.
Given an origin and a side-length it's a simple matter to iterate over each
side generating the necessary point:

.. literalinclude:: recipe_shapes1.py

Next we need a function which will iterate over the number of sides for each
required polygon, using the :func:`~picraft.vector.lines` function to generate
the points required to draw the shape. Then it's a simple matter to draw each
polygon in turn, wiping it before displaying the next one:

.. literalinclude:: recipe_shapes2.py


Animation
=========

This recipe demonstrates, in a series of steps, the construction of a
simplistic animation system in Minecraft. Our aim is to create a simple stone
cube which rotates about the X axis somewhere in the air. Our first script uses
:func:`~picraft.vector.vector_range` to obtain the coordinates of the cube,
then uses the :meth:`~picraft.vector.Vector.rotate` method to rotate them about
the X axis.

We represent the state of a frame of our animation as a dict which maps
coordinates (in the form of :class:`~picraft.vector.Vector` instances) to
:class:`~picraft.block.Block` instances:

.. literalinclude:: recipe_anim1.py

As you can see in the script above we draw the first frame, wait for a bit,
then wipe the frame by setting all coordinates in that frame's state back to
"air". Then we draw the second frame and wait for a bit.

Although this approach works, it's obviously very long winded for lots of
frames. What we want to do is calculate the state of each frame in a function.
This next version demonstrates this approach; we use a generator function to
yield the state of each frame in turn so we can iterate over the frames with
a simple ``for`` loop:

.. literalinclude:: recipe_anim2.py

That's more like it, but the updates aren't terribly fast despite using the
batch functionality. In order to improve this we should only update those
blocks which have actually changed between each frame. Thankfully, because
we're storing the state of each as a dict, this is quite easy:

.. literalinclude:: recipe_anim3.py

Note: this still isn't perfect. Ideally, we would identify contiguous blocks of
coordinates to be updated which have the same block and set them all at the
same time (which will utilize the :ref:`world.setBlocks` call for efficiency).
However, this is relatively complex to do well so I shall leave it as an
exercise for you, dear reader!


Minecraft TV
============

If you've got a Raspberry Pi camera module, you can build a TV to view a live
feed from the camera in the Minecraft world. Firstly we need to construct a
class which will accept JPEGs from the camera's MJPEG stream, and render them
as blocks in the Minecraft world. Then we need a class to construct the TV
model itself and enable interaction with it:

.. literalinclude:: recipe_tv.py

Don't expect to be able to recognize much in the Minecraft TV; the resolution
is extremely low and the color matching is far from perfect. Still, if you
point the camera at obvious blocks of primary colors and move it around slowly
you should see a similar result on the in-game display.

The script includes the ability to position and size the TV as you like, and
you may like to experiment with adding new controls to it!

.. _Martin O'Hanlon's excellent site: http://www.stuffaboutcode.com/
.. _auto-bridge project: http://www.stuffaboutcode.com/2013/02/raspberry-pi-minecraft-auto-bridge.html
.. _in-game piano project: http://www.stuffaboutcode.com/2013/06/raspberry-pi-minecraft-piano.html
