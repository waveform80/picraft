.. _quickstart:

===========
Quick Start
===========

Firstly, ensure that you have a `Minecraft game`_ running on your Pi. Now start
a terminal, start Python within the terminal, import the picraft library and
start a connection to the Minecraft world::

    >>> from picraft import *
    >>> world = World()

The :class:`~picraft.world.World` class is the usual starting point for picraft
scripts. It provides access to the blocks that make up the world, the players
within the world, methods to save and restore the state of the world, and the
ability to print things to the chat console. Let's start by printing something
to the console::

    >>> world.say('Hello, world!')

You should see "Hello, world!" appear in the chat console of the Minecraft
game.  Next, we can query where we're standing with the
:attr:`~picraft.player.HostPlayer.pos` attribute of the
:attr:`~picraft.world.World.player` attribute::

    >>> world.player.pos
    Vector(x=-2.49725, y=18.0, z=-4.21989)

This tells us that our character is standing at the 3-dimensional coordinates
-2.49, 18.0, -4.22 (approximately). In the Minecraft world, the X and Z
coordinates (the first and last) form the "ground plane". In other words you
can think of X as going left to right, and Z as going further to nearer. The Y
axis represents height (it goes up and down). We can find out our player's
coordinates rounded to the nearest block with the
:attr:`~picraft.player.HostPlayer.tile_pos` attribute::

    >>> world.player.tile_pos
    Vector(x=-3, y=18, z=-5)

Therefore, we can make our character jump in the air by adding a certain amount
to the player's Y coordinate. To do this we need to construct a
:class:`~picraft.vector.Vector` with a positive Y value and add it to the
:attr:`~picraft.player.HostPlayer.tile_pos` attribute::

    >>> world.player.tile_pos = world.player.tile_pos + Vector(y=5)

We can also use a Python short-hand for this::

    >>> world.player.tile_pos += Vector(y=5)

This demonstrates one way of constructing a :class:`~picraft.vector.Vector`.
We can also construct one by listing all 3 coordinates explicitly::

    >>> Vector(y=5)
    Vector(x=0, y=5, z=0)
    >>> Vector(0, 5, 0)
    Vector(x=0, y=5, z=0)

We can use the :attr:`~picraft.world.World.blocks` attribute to discover the
type of each block in the world. For example, we can find out what sort of
block we're currently standing on::

    >>> world.blocks[world.player.tile_pos - Vector(y=1)]
    <Block "grass" id=2 data=0>

We can assign values to this property to change the sort of block we're
standing on. In order to do this we need to construct a new
:class:`~picraft.block.Block` instance which can be done by specifying the
id manually, or by name::

    >>> Block(1)
    <Block "stone" id=1 data=0>
    >>> Block.from_name('stone')
    <Block "stone" id=1 data=0>

Now we'll change the block beneath our feet::

    >>> world.blocks[world.player.tile_pos - Vector(y=1)] = Block.from_name('stone')

We can query the state of many blocks surrounding us by providing a vector
slice to the :attr:`~picraft.world.World.blocks` attribute. To make things
a little easier we'll store the base position first::

    >>> v = world.player.tile_pos - Vector(y=1)
    >>> world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)]
    [<Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "stone" id=1 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>,
     <Block "grass" id=2 data=0>]

Note that the range provided (as with all ranges in Python) is `half-open`_,
which is to say that the lower end of the range is *inclusive* while the upper
end is *exclusive*. You can see this explicitly with the
:func:`~picraft.vector.vector_range` function::

    >>> v
    Vector(x=-2, y=14, z=3)
    >>> list(vector_range(v - Vector(1, 0, 1), v + Vector(2, 1, 2)))
    [Vector(x=-3, y=14, z=2),
     Vector(x=-2, y=14, z=2),
     Vector(x=-1, y=14, z=2),
     Vector(x=-3, y=14, z=3),
     Vector(x=-2, y=14, z=3),
     Vector(x=-1, y=14, z=3),
     Vector(x=-3, y=14, z=4),
     Vector(x=-2, y=14, z=4),
     Vector(x=-1, y=14, z=4)]

We can change the state of many blocks at once similarly by assigning a new
:class:`~picraft.block.Block` object to a slice of blocks::

    >>> v = world.player.tile_pos - Vector(y=1)
    >>> world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)] = Block.from_name('stone')

This is a relatively quick operation, as it only involves a single network
call. However, re-writing the state of multiple blocks with different values
is more time consuming::

    >>> world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)] = [
    ...     Block.from_name('wool', data=i) for i in range(9)]

You should notice that the example above takes a few seconds to process (each
block requires a separate network transaction and due to deficiencies in the
:ref:`Minecraft network protocol <protocol>`, each transaction takes a while to
execute). This can be accomplished considerably more quickly by batching
multiple requests together::

    >>> world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)] = Block.from_name('stone')
    >>> with world.connection.batch_start():
    ...     world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)] = [
    ...         Block.from_name('wool', data=i) for i in range(9)]

You should notice the example above executes considerably more quickly.
Finally, the state of the Minecraft world can be saved and restored easily with
the :attr:`~picraft.world.World.checkpoint` object::

    >>> world.checkpoint.save()
    >>> world.blocks[v - Vector(1, 0, 1):v + Vector(2, 1, 2)] = Block.from_name('stone')
    >>> world.checkpoint.restore()

This concludes the quick tour of the picraft library. Several recipes can be
found in the next section followed by the API reference.


.. _Minecraft game: https://www.raspberrypi.org/documentation/usage/minecraft/README.md
.. _half-open: http://python-history.blogspot.co.uk/2013/10/why-python-uses-0-based-indexing.html

