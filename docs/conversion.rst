.. _conversion:

====================
Conversion from mcpi
====================

If you have existing scripts that use the reference implementation
(minecraft-pi aka mcpi), and you wish to convert them to using the picraft
library, this section contains details and examples covering equivalent
functionality between the libraries.


Minecraft.create
================

Equivalent: :class:`~picraft.world.World`

To create a connection using default settings is similar in both libraries::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()

    >>> from picraft import World
    >>> w = World()

Creating a connection with an explicit hostname and port is also similar::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create('localhost', 4711)

    >>> from picraft import World
    >>> w = World('localhost', 4711)


Minecraft.getBlock
==================

See ``Minecraft.getBlockWithData`` below.


Minecraft.getBlockWithData
==========================

Equivalent: :attr:`~picraft.world.World.blocks`

Accessing the id of a block is rather different. There is no direct equivalent
to ``getBlock``, just ``getBlockWithData`` (as there's no difference in
operational cost so there's little point in retrieving a block id without the
data). In mcpi this is done by executing a method; in picraft this is done by
querying an attribute with a :class:`~picraft.vector.Vector`::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.getBlock(0, -1, 0)
    2
    >>> mc.getBlockWithData(0, -1, 0)
    Block(2, 0)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.blocks[Vector(0, -1, 0)]
    <Block "grass" id=2 data=0>

The id and data can be extracted from the :class:`~picraft.block.Block` tuple
that is returned::

    >>> w.blocks[Vector(0, -1, 0)].id
    2
    >>> w.blocks[Vector(0, -1, 0)].data
    0


Minecraft.setBlock
==================

Equivalent: :attr:`~picraft.world.World.blocks`

Setting the id (and optionally data) of a block is also rather different. In
picraft the same attribute is used as for accessing block ids; just *assign* a
:class:`~picraft.block.Block` instance to the attribute, instead of querying
it::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.getBlock(0, -1, 0)
    2
    >>> mc.setBlock(0, -1, 0, 1, 0)

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> w.blocks[Vector(0, -1, 0)]
    <Block "grass" id=2 data=0>
    >>> w.blocks[Vector(0, -1, 0)] = Block(1, 0)


Minecraft.setBlocks
===================

Equivalent: :attr:`~picraft.world.World.blocks`

Again, the same attribute as for ``setBlock`` is used for ``setBlocks``; just
pass a slice of :class:`vectors <picraft.vector.Vector>` instead of a single
vector (the example below shows an easy method of generating such a slice by
adding two vectors together for the upper end of the slice)::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.getBlock(0, -1, 0)
    2
    >>> mc.setBlocks(0, -1, 0, 0, 5, 0, 1, 0)

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> v = Vector(0, -1, 0)
    >>> w.blocks[v]
    <Block "grass" id=2 data=0>
    >>> w.blocks[v:v + Vector(1, 7, 1)] = Block(1, 0)


Minecraft.getHeight
===================

Equivalent: :attr:`~picraft.world.World.height`

Retrieving the height of the world in a specific location is done with an
attribute (like retrieving the id and type of blocks). Unlike mcpi, you
pass a full vector (of which the Y-coordinate is ignored), and the property
returns a full vector with the same X- and Z-coordinates, but the Y-coordinate
of the first non-air block from the top of the world::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.getHeight(0, 0)
    0

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.height[Vector(0, -10, 0)]
    Vector(x=0, y=0, z=0)


Minecraft.getPlayerEntityIds
============================

Equivalent: :attr:`~picraft.world.World.players`

The connected player's entity ids can be retrieved by iterating over the
:attr:`~picraft.world.World.players` attribute which acts as a mapping from
player id to :class:`~picraft.player.Player` instances::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.getPlayerEntityIds()
    [1]

    >>> from picraft import World
    >>> w = World()
    >>> list(w.players)
    [1]


Minecraft.saveCheckpoint
========================

Equivalent: :meth:`~picraft.world.Checkpoint.save`

Checkpoints can be saved in a couple of ways with picraft. Either you can
explicitly call the :meth:`~picraft.world.Checkpoint.save` method, or you
can use the :attr:`~picraft.world.World.checkpoint` attribute as a context
manager::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.saveCheckpoint()

    >>> from picraft import World
    >>> w = World()
    >>> w.checkpoint.save()

In the context manager case, the checkpoint will be saved upon entry to the
context and will only be restored if an exception occurs within the context::

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> with w.checkpoint:
    ...     # Do something with blocks...
    ...     w.blocks[Vector()] = Block.from_name('stone')


Minecraft.restoreCheckpoint
===========================

Equivalent: :meth:`~picraft.world.Checkpoint.restore`

As with saving a checkpoint, either you can call
:meth:`~picraft.world.Checkpoint.restore` directly::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.saveCheckpoint()
    >>> mc.restoreCheckpoint()

    >>> from picraft import World
    >>> w = World()
    >>> w.checkpoint.save()
    >>> w.checkpoint.restore()

Or you can use the context manager to restore the checkpoint automatically in
the case of an exception::

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> with w.checkpoint:
    ...     # Do something with blocks
    ...     w.blocks[Vector()] = Block.from_name('stone')
    ...     # Raising an exception within the block will implicitly
    ...     # cause the checkpoint to restore
    ...     raise Exception('roll back to the checkpoint')


Minecraft.postToChat
====================

Equivalent: :meth:`~picraft.world.World.say`

The ``postToChat`` method is simply replaced with the
:meth:`~picraft.world.World.say` method with the one exception that the latter
correctly recognizes line breaks in the message::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.create()
    >>> mc.postToChat('Hello world!')

    >>> from picraft import World
    >>> w = World()
    >>> w.say('Hello world!')

