# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft library for the Rasperry-Pi
# Copyright (c) 2013-2016 Dave Jones <dave@waveform.org.uk>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
The world module defines the :class:`World` class, which is the usual way of
starting a connection to a Minecraft server and which then provides various
attributes allowing the user to query and manipulate that world.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.world` directly.

The following items are defined in the module:


World
=====

.. autoclass:: World
    :members:


Checkpoint
==========

.. autoclass:: Checkpoint
    :members:


Camera
======

.. autoclass:: Camera
    :members:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from .exc import NotSupported
from .connection import Connection
from .player import HostPlayer, Players
from .block import Blocks
from .vector import Vector, vector_range
from .events import Events


class World(object):
    """
    Represents a Minecraft world.

    This is the primary class that users interact with. Construct an instance
    of this class, optionally specifying the *host* and *port* of the server
    (which default to "localhost" and 4711 respectively). Afterward, the
    instance can be used to query and manipulate the minecraft world of the
    connected game.

    The :meth:`say` method can be used to send commands to the console, while
    the :attr:`player` attribute can be used to manipulate or query the status
    of the player character in the world. The :attr:`players` attribute can be
    used to manipulate or query other players within the world (this object can
    be iterated over to discover players)::

        >>> from picraft import *
        >>> world = World()
        >>> len(world.players)
        1
        >>> world.say('Hello, world!')
    """

    def __init__(
            self, host='localhost', port=4711, timeout=1.0,
            ignore_errors=True):
        self._connection = Connection(host, port, timeout, ignore_errors)
        self._player = HostPlayer(self._connection)
        self._players = Players(self._connection)
        self._blocks = Blocks(self._connection)
        self._height = WorldHeight(self._connection)
        self._checkpoint = Checkpoint(self._connection)
        self._camera = Camera(self._connection)
        self._events = Events(self._connection)

    def __repr__(self):
        return '<World players=%d>' % len(self.players)

    @property
    def connection(self):
        """
        Represents the connection to the Minecraft server.

        The :class:`~picraft.connection.Connection` object contained in this
        attribute represents the connection to the Minecraft server and
        provides various methods for communicating with it. Users will very
        rarely need to access this attribute, except to use the
        :meth:`~picraft.connection.Connection.batch_start` method.
        """
        return self._connection

    @property
    def players(self):
        """
        Represents all player entities in the Minecraft world.

        This property can be queried to determine which players are currently
        in the Minecraft world. The property is a mapping of player id (an
        integer number) to a :class:`~picraft.player.Player` object which
        permits querying and manipulation of the player. The property supports
        many of the methods of dicts and can be iterated over like a dict::

            >>> len(world.players)
            1
            >>> list(world.players)
            [1]
            >>> world.players.keys()
            [1]
            >>> world.players[1]
            <picraft.player.Player at 0x7f2f91f38cd0>
            >>> world.players.values()
            [<picraft.player.Player at 0x7f2f91f38cd0>]
            >>> world.players.items()
            [(1, <picraft.player.Player at 0x7f2f91f38cd0>)]
            >>> for player in world.players:
            ...     print(player.tile_pos)
            ...
            -3,18,-5

        On the Raspberry Juice platform, you can also use player name to
        reference players::

            >>> world.players['my_player']
            <picraft.player.Player at 0x7f2f91f38cd0>
        """
        return self._players

    @property
    def player(self):
        """
        Represents the host player in the Minecraft world.

        The :class:`~picraft.player.HostPlayer` object returned by this
        attribute provides properties which can be used to query the status of,
        and manipulate the state of, the host player in the Minecraft world::

            >>> world.player.pos
            Vector(x=-2.49725, y=18.0, z=-4.21989)
            >>> world.player.tile_pos += Vector(y=50)
        """
        return self._player

    @property
    def height(self):
        """
        Represents the height of the Minecraft world.

        This property can be queried to determine the height of the world at
        any location. The property can be indexed with a single
        :class:`~picraft.vector.Vector`, in which case the height will be
        returned as a vector with the same X and Z coordinates, but a Y
        coordinate adjusted to the first non-air block from the top of the
        world::

            >>> world.height[Vector(0, -10, 0)]
            Vector(x=0, y=0, z=0)

        Alternatively, a slice of two vectors can be used. In this case, the
        property returns a sequence of :class:`~picraft.vector.Vector` objects
        each with their Y coordinates adjusted to the height of the world at
        the respective X and Z coordinates.
        """
        return self._height

    @property
    def camera(self):
        """
        Represents the camera of the Minecraft world.

        The :class:`Camera` object contained in this property permits control
        of the position of the virtual camera in the Minecraft world. For
        example, to position the camera directly above the host player::

            >>> world.camera.third_person(world.player)

        Alternatively, to see through the eyes of a specific player::

            >>> world.camera.first_person(world.players[2])

        .. warning::

            Camera control is only supported on Minecraft Pi edition.
        """
        return self._camera

    @property
    def blocks(self):
        """
        Represents the state of blocks in the Minecraft world.

        This property can be queried to determine the type of a block in the
        world, or can be set to alter the type of a block. The property can be
        indexed with a single :class:`~picraft.vector.Vector`, in which case
        the state of a single block is returned (or updated) as a
        :class:`~picraft.block.Block` object::

            >>> world.blocks[g.player.tile_pos]
            <Block "grass" id=2 data=0>

        Alternatively, a slice of vectors can be used. In this case, when
        querying the property, a sequence of :class:`~picraft.block.Block`
        objects is returned, When setting a slice of vectors you can either
        pass a sequence of :class:`~picraft.block.Block` objects or a single
        :class:`~picraft.block.Block` object::

            >>> world.blocks[Vector(0,0,0):Vector(2,1,1)]
            [<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>]
            >>> world.blocks[Vector(0,0,0):Vector(5,1,5)] = Block.from_name('grass')

        As with normal Python slices, the interval specified is `half-open`_.
        That is to say, it is inclusive of the lower vector, *exclusive* of the
        upper one. Hence, ``Vector():Vector(x=5,1,1)`` represents the
        coordinates (0,0,0) to (4,0,0). It is usually useful to specify the
        upper bound as the vector you want and then add one to it::

            >>> world.blocks[Vector():Vector(x=1) + 1]
            [<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>]
            >>> world.blocks[Vector():Vector(4,0,4) + 1] = Block.from_name('grass')

        .. _half-open: http://python-history.blogspot.co.uk/2013/10/why-python-uses-0-based-indexing.html

        Finally, you can query an arbitrary collection of vectors. In this case
        a sequence of blocks will be returned in the same order as the
        collection of vectors. You can also use this when setting blocks::

            >>> d = {
            ...     Vector(): Block('air'),
            ...     Vector(x=1): Block('air'),
            ...     Vector(z=1): Block('stone'),
            ...     }
            >>> l = list(d)
            >>> l
            [<Vector x=0, y=0, z=0>,<Vector x=1, y=0, z=0>,<Vector x=0, y=0, z=1>]
            >>> world.blocks[l]
            [<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>]
            >>> world.blocks[d.keys()] = d.values()

        .. warning::

            Querying or setting sequences of blocks can be extremely slow as a
            network transaction must be executed for each individual block.
            When setting a slice of blocks, this can be speeded up by
            specifying a single :class:`~picraft.block.Block` in which case one
            network transaction will occur to set all blocks in the slice.  The
            Raspberry Juice server also supports querying sequences of blocks
            with a single command (picraft will automatically use this).
            Additionally, :meth:`~picraft.connection.Connection.batch_start`
            can be used to speed up setting sequences of blocks (though not
            querying).
        """
        return self._blocks

    @property
    def events(self):
        """
        Provides an interface to poll events that occur in the Minecraft world.

        The :class:`~picraft.events.Events` object contained in this property
        provides methods for determining what is happening in the Minecraft
        world::

            >>> events = world.events.poll()
            >>> len(events)
            3
            >>> events[0]
            <BlockHitEvent pos=1,1,1 face="x+" player=1>
            >>> events[0].player.pos
            <Vector x=0.5, y=0.0, z=0.5>
        """
        return self._events

    @property
    def checkpoint(self):
        """
        Represents the Minecraft world checkpoint system.

        The :class:`Checkpoint` object contained in this attribute provides the
        ability to save and restore the state of the world at any time::

            >>> world.checkpoint.save()
            >>> world.blocks[Vector()] = Block.from_name('stone')
            >>> world.checkpoint.restore()
        """
        return self._checkpoint

    def say(self, message):
        """
        Displays *message* in the game's chat console.

        The *message* parameter must be a string (which may contain multiple
        lines). Each line of the message will be sent to the game's chat
        console and displayed immediately. For example::

            >>> world.say('Hello, world!')
            >>> world.say('The following player IDs exist:\\n%s' %
            ...     '\\n'.join(str(p) for p in world.players))
        """
        for line in message.splitlines():
            self.connection.send('chat.post(%s)' % line)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.connection.close()

    def _get_immutable(self):
        raise AttributeError(
                'reading immutable is not supported by the server')
    def _set_immutable(self, value):
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot change world settings on server version: %s' %
                self._connection.server_version)
        self._connection.send('world.setting(world_immutable,%d)' % bool(value))
    immutable = property(_get_immutable, _set_immutable,
        doc="""\
        Write-only property which sets whether the world is changeable.

        .. warning::

            World settings are only supported on Minecraft Pi edition.

        .. note::

            Unfortunately, the underlying protocol provides no means of reading
            a world setting, so this property is write-only (attempting to
            query it will result in an :exc:`AttributeError` being raised).
        """)

    def _get_nametags_visible(self):
        raise AttributeError(
                'reading nametags_visible is not supported by the server')
    def _set_nametags_visible(self, value):
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot change world settings on server version: %s' %
                self._connection.server_version)
        self._connection.send('world.setting(nametags_visible,%d)' % bool(value))
    nametags_visible = property(_get_nametags_visible, _set_nametags_visible,
        doc="""\
        Write-only property which sets whether players' nametags are visible.

        .. warning::

            World settings are only supported on Minecraft Pi edition.

        .. note::

            Unfortunately, the underlying protocol provides no means of reading
            a world setting, so this property is write-only (attempting to
            query it will result in an :exc:`AttributeError` being raised).
        """)


class WorldHeight(object):
    """
    This class implements the :attr:`~picraft.world.World.heights` attribute.
    """

    def __init__(self, connection):
        self._connection = connection

    def __repr__(self):
        return '<WorldHeight>'

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [
                Vector(v.x, int(self._connection.transact(
                    'world.getHeight(%d,%d)' % (v.x, v.z))), v.z)
                for v in vector_range(index.start, index.stop)
                ]
        else:
            return Vector(index.x, int(self._connection.transact(
                'world.getHeight(%d,%d)' % (index.x, index.z))), index.z)


class Checkpoint(object):
    """
    Permits restoring the world state from a prior save.

    This class provides methods for storing the state of the Minecraft world,
    and restoring the saved state at a later time. The :meth:`save` method
    saves the state of the world, and the :meth:`restore` method restores
    the saved state.

    This class can be used as a context manager to take a checkpoint, make
    modifications to the world, and roll them back if an exception occurs.
    For example, the following code will ultimately do nothing because an
    exception occurs after the alteration::

        >>> from picraft import *
        >>> w = World()
        >>> with w.checkpoint:
        ...     w.blocks[w.player.tile_pos - Vector(y=1)] = Block.from_name('stone')
        ...     raise Exception()

    .. warning::

        Checkpoints are only supported on Minecraft Pi edition.

    .. warning::

        Minecraft only permits a single checkpoint to be stored at any given
        time. There is no capability to save multiple checkpoints and no way of
        checking whether one currently exists. Therefore, storing a checkpoint
        may overwrite an older checkpoint without warning.

    .. note::
        Checkpoints don't work *within* batches as the checkpoint save will be
        batched along with everything else. That said, a checkpoint can be used
        *outside* a batch to roll the entire thing back if it fails::

            >>> v = w.player.tile_pos - Vector(y=1)
            >>> with w.checkpoint:
            ...     with w.connection.batch_start():
            ...         w.blocks[v - Vector(2, 0, 2):v + Vector(2, 1, 2)] = [
            ...             Block.from_name('wool', data=i) for i in range(16)]
    """

    def __init__(self, connection):
        self._connection = connection

    def __repr__(self):
        return '<Checkpoint>'

    def save(self):
        """
        Save the state of the Minecraft world, overwriting any prior checkpoint
        state.
        """
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot save checkpoint on server version: %s' %
                self._connection.server_version)
        self._connection.send('world.checkpoint.save()')

    def restore(self):
        """
        Restore the state of the Minecraft world from a previously saved
        checkpoint.  No facility is provided to determine whether a prior
        checkpoint is available (the underlying network protocol doesn't permit
        this).
        """
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot restore checkpoint on server version: %s' %
                self._connection.server_version)
        self._connection.send('world.checkpoint.restore()')

    def __enter__(self):
        self.save()

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            self.restore()


class Camera(object):
    """
    This class implements the :attr:`~picraft.world.World.camera` attribute.
    """

    def __init__(self, connection):
        self._connection = connection

    def __repr__(self):
        return '<Camera>'

    def _get_pos(self):
        raise AttributeError(
                'reading camera position is not supported by server')
    def _set_pos(self, value):
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot position camera on server version: %s' %
                    self._connection.server_version)
        self._connection.send('camera.mode.setFixed()')
        self._connection.send('camera.setPos(%d,%d,%d)' % (value.x, value.y, value.z))
    pos = property(_get_pos, _set_pos, doc="""\
        Write-only property which sets the camera's absolute position in the
        world.

        .. note::

            Unfortunately, the underlying protocol provides no means of reading
            this setting, so this property is write-only (attempting to query
            it will result in an :exc:`AttributeError` being raised).
        """)

    def third_person(self, player):
        """
        Causes the camera to follow the specified player from above. The
        *player* can be the :attr:`~World.player` attribute (representing the
        host player) or an attribute retrieved from the :attr:`~World.players`
        list. For example::

            >>> from picraft import World
            >>> w = World()
            >>> w.camera.third_person(w.player)
            >>> w.camera.third_person(w.players[1])
        """
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot position camera on server version: %s' %
                self._connection.server_version)
        if isinstance(player, HostPlayer):
            self._connection.send('camera.mode.setFollow()')
        else:
            self._connection.send('camera.mode.setFollow(%d)' % player.player_id)

    def first_person(self, player):
        """
        Causes the camera to view the world through the eyes of the specified
        player. The *player* can be the :attr:`~World.player` attribute
        (representing the host player) or an attribute retrieved from the
        :attr:`~World.players` list. For example::

            >>> from picraft import World
            >>> w = World()
            >>> w.camera.first_person(w.player)
            >>> w.camera.first_person(w.players[1])
        """
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot position camera on server version: %s' %
                self._connection.server_version)
        if isinstance(player, HostPlayer):
            self._connection.send('camera.mode.setNormal()')
        else:
            self._connection.send('camera.mode.setNormal(%d)' % player.player_id)

