# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft library for the Rasperry-Pi
# Copyright (c) 2013-2015 Dave Jones <dave@waveform.org.uk>
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

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from .connection import Connection
from .vector import Vector


class Entity(object):
    """
    Represents a player within the game world.

    Players are uniquely identified by their :attr:`player_id`. Instances
    of this class are available from the :attr:`Game.players` collection. It
    provides properties to query and manipulate the position and settings of
    the player.
    """
    def __init__(self, connection, player_id):
        self._connection = connection
        self._player_id = player_id


class Player(object):
    """
    Represents the host player within the game world.

    An instance of this class is accessible as the :attr:`Game.player`
    attribute. It provides properties to query and manipulate the position
    and settings of the host player.
    """
    def __init__(self, connection):
        self._connection = connection

    def _get_pos(self):
        return Vector.from_string(
            self._connection.transact('player.getPos()'),
            type=float)
    def _set_pos(self, value):
        self._connection.send('player.setPos(%s)' % str(value))
    pos = property(
        lambda self: self._get_pos(),
        lambda self: self._set_pos(),
        doc="""
        The precise position of the host player within the world.

        This property returns the position of the host player within the
        Minecraft world, as a :class:`Vector` instance. This is the *precise*
        position of the player including decimal places (representing portions
        of a tile). You can assign to this property to reposition the player.
        """)

    def _get_tile_pos(self):
        return Vector.from_string(self._connection.transact('player.getTile()'))
    def _set_tile_pos(self, value):
        self._connection.send('player.setTile(%s)' % str(value))
    tile_pos = property(
        lambda self: self._get_tile_pos(),
        lambda self: self._set_tile_pos(),
        doc="""
        The position of the host player within the world to the nearest block.

        This property returns the position of the host player in the Minecraft
        world to the nearest block, as a :class:`Vector` instance. You can
        assign to this property to reposition the player.
        """)


class Game(object):
    """
    Represents a Minecraft game.

    This is the primary class that users interact with. Construct an instance
    of this class, optionally specifying the *host* and *port* of the server
    (which default to "localhost" and 4711 respectively). Afterward, the
    instance can be used to query and manipulate the minecraft world of the
    connected game.

    The :meth:`say` method can be used to send commands to the console, while
    the :attr:`player` attribute can be used to manipulate or query the status
    of the player character in the game. The :attr:`entities` attribute can be
    used to manipulate or query other objects within the game (this object can
    be iterated over to discover entities).
    """
    def __init__(self, host='localhost', port=4711):
        self._connection = Connection(host, port)
        self._player = Player(self)

    @property
    def connection(self):
        """
        Represents the connection to the Minecraft server.

        The :class:`Connection` instance contained in this attribute represents
        the connection to the Minecraft server and provides various methods for
        communicating with it. Users will very rarely need to access this
        attribute unless they wish to manually manipulate the Minecraft Pi API.
        """
        return self._connection

    @property
    def player(self):
        """
        Represents the host player in the Minecraft world.

        The :class:`Player` instance returned by this attribute provides
        properties which can be used to query the status of, and manipulate
        the state of, the host player in the Minecraft world.
        """
        return self._player

    def close(self):
        """
        Closes the connection to the game server.

        After this method is called, the game connection is closed and no
        further requests can be made. This method is implicitly called when
        the class is used as a context manager.
        """
        self.connection.close()

    def say(self, message):
        """
        Displays *message* in the game's chat console.

        The *message* parameter must be a string (which may contain multiple
        lines). Each line of the message will be sent to the game's chat
        console and displayed immediately.
        """
        for line in message.splitlines():
            self.connection.send('chat.post(%s)' % line)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

