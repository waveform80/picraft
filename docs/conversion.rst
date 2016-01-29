.. _conversion:

====================
Conversion from mcpi
====================

If you have existing scripts that use the mcpi implementation, and you wish to
convert them to using the picraft library, this section contains details and
examples covering equivalent functionality between the libraries.


Minecraft.create
================

Equivalent: :class:`~picraft.world.World`

To create a connection using default settings is similar in both libraries::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()

    >>> from picraft import World
    >>> w = World()

Creating a connection with an explicit hostname and port is also similar::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create('localhost', 4711)

    >>> from picraft import World
    >>> w = World('localhost', 4711)


Minecraft.getBlock
==================

See :ref:`Minecraft.getBlockWithData` below.


Minecraft.getBlocks
===================

Equivalent: :attr:`~picraft.world.World.blocks`

This method only works with the `Raspberry Juice`_ mod for the PC version of
Minecraft. In picraft simply query the :attr:`~picraft.world.World.blocks`
attribute with a slice of vectors, just as with the equivalent to
:ref:`Minecraft.setBlocks` below::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.getBlocks(0, -1, 0, 0, 5, 0)
    [2, 2, 2, 2, 2, 2, 2]

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> v1 = Vector(0, -1, 0)
    >>> v2 = Vector(0, 5, 0)
    >>> w.blocks[v1:v2 + 1]
    [<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>,
    <Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>,
    <Block "grass" id=2 data=0>]

.. note::

    In picraft, this method will work with both Raspberry Juice and Minecraft
    Pi Edition, but the efficient ``getBlocks`` call will only be used when
    picraft detects it is connected to a Raspberry Juice server.

.. warning::

    There is currently no equivalent to ``getBlockWithData`` that operates over
    multiple blocks, so blocks returned by querying in this manner only have a
    valid :attr:`~picraft.block.Block.id` field; the
    :attr:`~picraft.block.Block.data` attribute is always 0.

.. _Raspberry Juice: http://dev.bukkit.org/bukkit-plugins/raspberryjuice/


.. _Minecraft.getBlockWithData:

Minecraft.getBlockWithData
==========================

Equivalent: :attr:`~picraft.world.World.blocks`

There is no direct equivalent to ``getBlock``, just ``getBlockWithData`` (as
there's no difference in operational cost so there's little point in retrieving
a block id without the data). In mcpi this is done by executing a method; in
picraft this is done by querying an attribute with a
:class:`~picraft.vector.Vector`::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
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

    >>> b = w.blocks[Vector(0, -1, 0)]
    >>> b.id
    2
    >>> b.data
    0


Minecraft.setBlock
==================

Equivalent: :attr:`~picraft.world.World.blocks`

In picraft the same attribute is used as for accessing block ids; just *assign*
a :class:`~picraft.block.Block` instance to the attribute, instead of querying
it::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.getBlock(0, -1, 0)
    2
    >>> mc.setBlock(0, -1, 0, 1, 0)

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> w.blocks[Vector(0, -1, 0)]
    <Block "grass" id=2 data=0>
    >>> w.blocks[Vector(0, -1, 0)] = Block(1, 0)


.. _Minecraft.setBlocks:

Minecraft.setBlocks
===================

Equivalent: :attr:`~picraft.world.World.blocks`

The same attribute as for ``setBlock`` is used for ``setBlocks``; just pass a
slice of :class:`vectors <picraft.vector.Vector>` instead of a single vector
(the example below shows an easy method of generating such a slice by adding 1
to a vector for the upper end of the slice)::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.getBlock(0, -1, 0)
    2
    >>> mc.setBlocks(0, -1, 0, 0, 5, 0, 1, 0)

    >>> from picraft import World, Vector, Block
    >>> w = World()
    >>> v1 = Vector(0, -1, 0)
    >>> v2 = Vector(0, 5, 0)
    >>> w.blocks[v]
    <Block "grass" id=2 data=0>
    >>> w.blocks[v1:v2 + 1] = Block(1, 0)


Minecraft.getHeight
===================

Equivalent: :attr:`~picraft.world.World.height`

Retrieving the height of the world in a specific location is done with an
attribute (like retrieving the id and type of blocks). Unlike mcpi, you
pass a full vector (of which the Y-coordinate is ignored), and the property
returns a full vector with the same X- and Z-coordinates, but the Y-coordinate
of the first non-air block from the top of the world::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
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
    >>> mc = minecraft.Minecraft.create()
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
    >>> mc = minecraft.Minecraft.create()
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
    >>> mc = minecraft.Minecraft.create()
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
    >>> mc = minecraft.Minecraft.create()
    >>> mc.postToChat('Hello world!')

    >>> from picraft import World
    >>> w = World()
    >>> w.say('Hello world!')


Minecraft.setting
=================

Equivalent: :attr:`~picraft.world.World.immutable` and
:attr:`~picraft.world.World.nametags_visible`

The ``setting`` method is replaced with (write-only) properties with the
equivalent names to the settings that can be used::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.setting('world_immutable', True)
    >>> mc.setting('nametags_visible', True)

    >>> from picraft import World
    >>> w = World()
    >>> w.immutable = True
    >>> w.nametags_visible = True


.. _Minecraft.player.getPos:

Minecraft.player.getPos
=======================

Equivalent: :attr:`~picraft.player.HostPlayer.pos`

The ``player.getPos`` and ``player.setPos`` methods are replaced with the
:attr:`~picraft.player.HostPlayer.pos` attribute which returns a
:class:`~picraft.vector.Vector` of floats and accepts the same to move the host
player::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.getPos()
    Vec3(12.7743,12.0,-8.39158)
    >>> mc.player.setPos(12,12,-8)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.player.pos
    Vector(x=12.7743, y=12.0, z=-8.39158)
    >>> w.player.pos = Vector(12, 12, -8)

One advantage of this implementation is that adjusting the player's position
relative to their current one becomes simple::

    >>> w.player.pos += Vector(y=20)


Minecraft.player.setPos
=======================

See :ref:`Minecraft.player.getPos` above.


.. _Minecraft.player.getTilePos:

Minecraft.player.getTilePos
===========================

Equivalent: :attr:`~picraft.player.HostPlayer.tile_pos`

The ``player.getTilePos`` and ``player.setTilePos`` methods are replaced with
the :attr:`~picraft.player.HostPlayer.tile_pos` attribute which returns a
:class:`~picraft.vector.Vector` of ints, and accepts the same to move the
host player::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.getTilePos()
    Vec3(12,12,-9)
    >>> mc.player.setTilePos(12, 12, -8)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.player.tile_pos
    Vector(x=12, y=12, z=-9)
    >>> w.player.tile_pos += Vector(y=20)


Minecraft.player.setTilePos
===========================

See :ref:`Minecraft.player.getTilePos` above.


Minecraft.player.setting
========================

Equivalent: :attr:`~picraft.player.HostPlayer.autojump`

The ``player.setting`` method is replaced with the write-only
:attr:`~picraft.player.HostPlayer.autojump` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.setting('autojump', False)

    >>> from picraft import World
    >>> w = World()
    >>> w.player.autojump = False


Minecraft.player.getRotation
============================

Equivalent: :attr:`~picraft.player.HostPlayer.heading`

The ``player.getRotation`` method is replaced with the read-only
:attr:`~picraft.player.HostPlayer.heading` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.getRotation()
    49.048615

    >>> from picraft import World
    >>> w = World()
    >>> w.player.heading
    49.048615


Minecraft.player.getPitch
=========================

Equivalent: :attr:`~picraft.player.HostPlayer.pitch`

The ``player.getPitch`` method is replaced with the read-only
:attr:`~picraft.player.HostPlayer.pitch` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.getPitch()
    4.3500223

    >>> from picraft import World
    >>> w = World()
    >>> w.player.pitch
    4.3500223


Minecraft.player.getDirection
=============================

Equivalent: :attr:`~picraft.player.HostPlayer.direction`

The ``player.getDirection`` method is replaced with the read-only
:attr:`~picraft.player.HostPlayer.direction` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.player.getDirection()
    Vec3(0.1429840348766887,-0.3263934845430674,0.934356922711132)

    >>> from picraft import World
    >>> w = World()
    >>> w.player.direction
    Vector(x=0.1429840348766887, y=-0.3263934845430674, z=0.934356922711132)


.. _Minecraft.entity.getPos:

Minecraft.entity.getPos
=======================

Equivalent: :attr:`~picraft.player.Player.pos`

The ``entity.getPos`` and ``entity.setPos`` methods are replaced with the
:attr:`~picraft.player.Player.pos` attribute. Access the relevant
:class:`~picraft.player.Player` instance by indexing the
:attr:`~picraft.world.World.players` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.entity.getPos(1)
    Vec3(12.7743,12.0,-8.39158)
    >>> mc.entity.setPos(1, 12, 12, -8)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.players[1].pos
    Vector(x=12.7743, y=12.0, z=-8.39158)
    >>> w.players[1].pos = Vector(12, 12, -8)


Minecraft.entity.setPos
=======================

See :ref:`Minecraft.entity.getPos` above.


.. _Minecraft.entity.getTilePos:

Minecraft.entity.getTilePos
===========================

Equivalent: :attr:`~picraft.player.Player.tile_pos`

The ``entity.getTilePos`` and ``entity.setTilePos`` methods are replaced with
the :attr:`~picraft.player.Player.tile_pos` attribute. Access the relevant
:class:`~picraft.player.Player` instance by indexing the
:attr:`~picraft.world.World.players` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.entity.getTilePos(1)
    Vec3(12,12,-9)
    >>> mc.entity.setTilePos(1, 12, 12, -8)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.players[1].tile_pos
    Vector(x=12, y=12, z=-9)
    >>> w.players[1].tile_pos += Vector(y=20)


Minecraft.entity.setTilePos
===========================

See :ref:`Minecraft.entity.getTilePos` above.


Minecraft.entity.getRotation
============================

Equivalent: :attr:`~picraft.player.Player.heading`

The ``entity.getRotation`` method is replaced with the read-only
:attr:`~picraft.player.Player.heading` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.entity.getRotation(213)
    49.048615

    >>> from picraft import World
    >>> w = World()
    >>> w.players[213].heading
    49.048615


Minecraft.entity.getPitch
=========================

Equivalent: :attr:`~picraft.player.Player.pitch`

The ``entity.getPitch`` method is replaced with the read-only
:attr:`~picraft.player.Player.pitch` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.entity.getPitch(213)
    4.3500223

    >>> from picraft import World
    >>> w = World()
    >>> w.players[213].pitch
    4.3500223


Minecraft.entity.getDirection
=============================

Equivalent: :attr:`~picraft.player.Player.direction`

The ``entity.getDirection`` method is replaced with the read-only
:attr:`~picraft.player.Player.duration` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.entity.getDirection(213)
    Vec3(0.1429840348766887,-0.3263934845430674,0.934356922711132)

    >>> from picraft import World
    >>> w = World()
    >>> w.players[213].direction
    Vector(x=0.1429840348766887, y=-0.3263934845430674, z=0.934356922711132)


Minecraft.camera.setNormal
==========================

Equivalent: :meth:`~picraft.world.Camera.first_person`

The :attr:`~picraft.world.World.camera` attribute in picraft holds a
:class:`~picraft.world.Camera` instance which controls the camera in the
Minecraft world. The :meth:`~picraft.world.Camera.first_person` method can be
used to set the camera to view the world through the eyes of the specified
player. The player is specified as the world's
:attr:`~picraft.world.World.player` attribute, or as a player retrieved from
the :attr:`~picraft.world.World.players` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.camera.setNormal()
    >>> mc.camera.setNormal(2)

    >>> from picraft import World
    >>> w = World()
    >>> w.camera.first_person(w.player)
    >>> w.camera.first_person(w.players[2])


Minecraft.camera.setFollow
==========================

Equivalent: :meth:`~picraft.world.Camera.third_person`

The :attr:`~picraft.world.World.camera` attribute in picraft holds a
:class:`~picraft.world.Camera` instance which controls the camera in the
Minecraft world. The :meth:`~picraft.world.Camera.third_person` method can be
used to set the camera to view the specified player from above.  The player is
specified as the world's :attr:`~picraft.world.World.player` attribute, or as a
player retrieved from the :attr:`~picraft.world.World.players` attribute::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.camera.setFollow()
    >>> mc.camera.setNormal(1)

    >>> from picraft import World
    >>> w = World()
    >>> w.camera.third_person(w.player)
    >>> w.camera.third_person(w.players[1])


.. _Minecraft.camera.setFixed:

Minecraft.camera.setFixed
=========================

Equivalent: :attr:`~picraft.world.Camera.pos`

The :attr:`~picraft.world.Camera.pos` attribute can be passed a
:class:`~picraft.vector.Vector` instance to specify the absolute position of
the camera. The camera will be pointing straight down (y=-1) from the given
position and will not move to follow any entity::

    >>> import mcpi.minecraft as minecraft
    >>> mc = minecraft.Minecraft.create()
    >>> mc.camera.setFixed()
    >>> mc.camera.setPos(0,20,0)

    >>> from picraft import World, Vector
    >>> w = World()
    >>> w.camera.pos = Vector(0, 20, 0)


Minecraft.camera.setPos
=======================

See :ref:`Minecraft.camera.setFixed` above.


Minecraft.block.Block
=====================

Equivalent: :class:`~picraft.block.Block`

The :class:`~picraft.block.Block` class in picraft is similar to the ``Block``
class in mcpi but with one major difference: in picraft a ``Block`` instance
is a tuple descendent and therefore immutable (you cannot change the id or
data attributes of a ``Block`` instance).

This may seem like an arbitrary barrier, but firstly its quite rare to
adjust the the id or data attribute (it's rather more common to just overwrite
a block in the world with an entirely new type), and secondly this change
permits blocks to be used as keys in a Python dictionary, or to be stored
in a set.

The :class:`~picraft.block.Block` class also provides several means of
construction, and additional properties::

    >>> from picraft import Block
    >>> Block(1, 0)
    <Block "stone" id=1 data=0>
    >>> Block(35, 1)
    <Block "wool" id=35 data=1>
    >>> Block.from_name('wool', data=1).description
    u'Orange Wool'
    >>> Block.from_color('#ffffff').description
    u'White Wool'
