.. _recipes:

=======
Recipes
=======


Vectors
=======

Vectors are a crucial part of working with picraft; sufficiently important to
demand their own section

The picraft :class:`~picraft.vector.Vector` class is extremely flexible and
supports a wide variety of operations. All Python's built-in operations
(addition, subtraction, division, multiplication, modulus, absolute, bitwise
operations, etc.) are supported between two vectors, in which case the
operation is performed element-wise. In other words, adding two vectors ``A``
and ``B`` produces a new vector with its ``x`` attribute set to ``A.x + B.x``,
its ``y`` attribute set to ``A.y + B.y`` and so on::

    >>> from picraft import *
    >>> Vector(1, 1, 0) + Vector(1, 0, 1)
    Vector(x=2, y=1, z=1)

.. image:: vector1.*
    :align: center

Likewise for subtraction, multiplication, etc.::

    >>> p = Vector(1, 2, 3)
    >>> q = Vector(3, 2, 1)
    >>> p - q
    Vector(x=-2, y=0, z=2)
    >>> p * q
    Vector(x=3, y=4, z=3)
    >>> p % q
    Vector(x=1, y=0, z=0)

.. image:: vector2.*
    :align: center

Vectors also support several operations between themselves and a scalar value.
In this case the operation with the scalar is applied to each element of the
vector. For example, multiplying a vector by the number 2 will return a new
vector with every element of the original multiplied by 2::

    >>> p * 2
    Vector(x=2, y=4, z=6)
    >>> p + 2
    Vector(x=3, y=4, z=5)
    >>> p // 2
    Vector(x=0, y=1, z=1)

.. image:: vector3.*
    :align: center

Vectors also support several of Python's built-in functions::

    >>> abs(Vector(-1, 0, 1))
    Vector(x=1, y=0, z=1)
    >>> pow(Vector(1, 2, 3), 2)
    Vector(x=1, y=4, z=9)
    >>> import math
    >>> math.trunc(Vector(1.5, 2.3, 3.7))
    Vector(x=1, y=2, z=3)

Some built-in functions can't be directly supported, in which case equivalently
named methods are provided::

    >>> p = Vector(1.5, 2.3, 3.7)
    >>> p.round()
    Vector(x=2, y=2, z=4)
    >>> p.ceil()
    Vector(x=2, y=3, z=4)
    >>> p.floor()
    Vector(x=1, y=2, z=3)

.. image:: vector4.*
    :align: center

Several vector short-hands are also provided. One for the unit vector along
each of the three axes (X, Y, and Z), one for the origin (O), and finally V
which is simply a short-hand for Vector itself. Obviously, these can be used
to simplify many vector-related operations::

    >>> X
    Vector(x=1, y=0, z=0)
    >>> X + Y
    Vector(x=1, y=1, z=0)
    >>> Vector(1, 2, 3) + X
    Vector(x=2, y=2, z=3)
    >>> V(1, 2, 3) + (4 * Y)
    Vector(x=1, y=6, z=3)

From the paragraphs above it should be relatively easy to see how one can
implement vector translation and vector scaling using everyday operations like
addition, subtraction, multiplication and divsion. The third major
transformation usually required of vectors, rotation, is a little harder. For
this, the :meth:`~picraft.vector.Vector.rotate` method is provided. This takes
two mandatory arguments: the number of degrees to rotate, and a vector
specifying the axis about which to rotate (it is recommended that this is
specified as a keyword argument for code clarity). For example::

    >>> Vector(1, 2, 3).rotate(90, about=X)
    Vector(x=1.0, y=-3.0, z=2.0)
    >>> Vector(1, 2, 3).rotate(180, about=Y)
    Vector(x=-0.9999999999999997, y=2, z=-3.0)
    >>> Vector(1, 2, 3).rotate(180, about=Y).round()
    Vector(x=-1.0, y=2.0, z=-3.0)
    >>> X.rotate(180, about=X + Y).round()
    Vector(x=-0.0, y=1.0, z=-0.0)

A third optional argument to rotate, *origin*, permits rotation about an
arbitrary line. The line passes through the point specified by *origin* and
runs in the direction of the axis specified by *about*. Naturally, *origin*
defaults to the origin (0, 0, 0)::

    >>> Vector(1, 0, 0).rotate(180, about=Y, origin=2 * X).round()
    Vector(x=3.0, y=0.0, z=0.0)
    >>> O.rotate(90, about=Y, origin=X).round()
    Vector(x=1.0, y=0.0, z=1.0)




Player Position
===============

The player's position can be easily queried with the
:attr:`~picraft.player.Player.pos` attribute. The value is a
:class:`~picraft.vector.Vector`. For example, on the command line::

    >>> world = World()
    >>> world.player.pos
    Vector(x=2.3, y=1.1, z=-0.81)

Teleporting the player is as simple as assigning a new vector to the player
position.  Here we teleport the player into the air by adding 50 to the Y-axis
of the player's current position (remember that in the Minecraft world, the
Y-axis goes up/down)::

    >>> world.player.pos = world.player.pos + Vector(y=50)

Or we can use a bit of Python short-hand for this::

    >>> world.player.pos += Vector(y=50)

If you want the player position to the nearest block use the
:attr:`~picraft.player.Player.tile_pos` instead::

    >>> world.player.pos
    Vector(x=2, y=1, z=-1)


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
:func:`~picraft.vector.vector_range` to obtain the coordinates of all blocks
within the cube, then uses the :meth:`~picraft.vector.Vector.rotate` method to
rotate them about the X axis:

.. literalinclude:: recipe_anim1.py

As you can see in the script above we draw the first frame, wait for a bit,
then wipe the frame by setting all coordinates in that frame's state back to
"air". Then we draw the second frame and wait for a bit.

Although this approach works, it's obviously very long winded for lots of
frames. What we want to do is calculate the state of each frame in a function.
This next version demonstrates this approach; we use a generator function to
yield the state of each frame in turn so we can iterate over the frames with
a simple ``for`` loop.

We represent the state of a frame of our animation as a dict which maps
coordinates (in the form of :class:`~picraft.vector.Vector` instances) to
:class:`~picraft.block.Block` instances:

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
