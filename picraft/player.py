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


from .vector import Vector


class Players(object):
    """
    Represents the players currently present in the game world.

    This class presents a mapping of player-id to :class:`Player` instance.
    The mapping is read-only, but supports many of the methods of a regular
    dict.
    """

    def __init__(self, connection):
        self._connection = connection
        self._cache = {}

    def _refresh(self):
        self._cache = {
            pid: self._cache.get(pid, Player(self._connection, pid))
            for pid in (
                int(i) for i in
                self._connection.transact('world.getPlayerIds()').split('|')
                )
            }

    def __len__(self):
        self._refresh()
        return len(self._cache)

    def __contains__(self, key):
        self._refresh()
        return key in self._cache

    def __iter__(self):
        self._refresh()
        return iter(self._cache)

    def __getitem__(self, key):
        self._refresh()
        return self._cache[key]

    def keys(self):
        self._refresh()
        return self._cache.keys()

    def values(self):
        self._refresh()
        return self._cache.values()

    def items(self):
        self._refresh()
        return self._cache.items()


class Player(object):
    """
    Represents a player within the game world.

    Players are uniquely identified by their :attr:`player_id`. Instances
    of this class are available from the :attr:`Game.players` mapping. It
    provides properties to query and manipulate the position and settings of
    the player.
    """

    def __init__(self, connection, player_id):
        self._connection = connection
        self._player_id = player_id

    def _get_pos(self):
        return Vector.from_string(
            self._connection.transact('entity.getPos(%d)' % self._player_id),
            type=float)
    def _set_pos(self, value):
        self._connection.send('entity.setPos(%d,%s)' % (self._player_id, value))
    pos = property(
        lambda self: self._get_pos(),
        lambda self, value: self._set_pos(value),
        doc="""
        The precise position of the player within the world.

        This property returns the position of the selected player within the
        Minecraft world, as a :class:`Vector` instance. This is the *precise*
        position of the player including decimal places (representing portions
        of a tile). You can assign to this property to reposition the player.
        """)

    def _get_tile_pos(self):
        return Vector.from_string(
            self._connection.transact('entity.getTile(%d)' % self._player_id))
    def _set_tile_pos(self, value):
        self._connection.send('entity.setTile(%d,%s)' % (self._player_id, value))
    tile_pos = property(
        lambda self: self._get_tile_pos(),
        lambda self, value: self._set_tile_pos(value),
        doc="""
        The position of the player within the world to the nearest block.

        This property returns the position of the selected player in the
        Minecraft world to the nearest block, as a :class:`Vector` instance.
        You can assign to this property to reposition the player.
        """)


class HostPlayer(object):
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
        lambda self, value: self._set_pos(value),
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
        lambda self, value: self._set_tile_pos(value),
        doc="""
        The position of the host player within the world to the nearest block.

        This property returns the position of the host player in the Minecraft
        world to the nearest block, as a :class:`Vector` instance. You can
        assign to this property to reposition the player.
        """)

