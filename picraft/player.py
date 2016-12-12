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
The player module defines the :class:`Players` class, which is available via
the :attr:`~picraft.world.World.players` attribute, the :class:`Player` class,
which represents an arbitrary player in the world, and the :class:`HostPlayer`
class which represents the player on the host machine (accessible via the
:attr:`~picraft.world.World.player` attribute).

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.player` directly.

The following items are defined in the module:


Player
======

.. autoclass:: Player
    :inherited-members:
    :members:


HostPlayer
==========

.. autoclass:: HostPlayer
    :inherited-members:
    :members:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from .exc import ConnectionError, NotSupported
from .vector import Vector, X, Y, Z


class Players(object):
    """
    Thie class implements the :attr:`~picraft.world.World.players` attribute.
    """

    def __init__(self, connection):
        self._connection = connection
        self._cache = {}

    def __repr__(self):
        self._refresh()
        return '<Players keys={%s}>' % (', '.join(str(i) for i in self._cache))

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
        try:
            return self._cache[key]
        except KeyError as e:
            if self._connection.server_version == 'raspberry-juice':
                try:
                    key = int(self._connection.transact('world.getPlayerId(%s)' % key))
                except ConnectionError:
                    # Ignore failed lookups and fall-through to the re-raise
                    pass
                else:
                    return self._cache[key]
            raise e

    def keys(self):
        self._refresh()
        return self._cache.keys()

    def values(self):
        self._refresh()
        return self._cache.values()

    def items(self):
        self._refresh()
        return self._cache.items()


class BasePlayer(object):
    """
    Base class for players.
    """

    def __init__(self, connection, prefix, player_id):
        self._connection = connection
        self._player_id = player_id
        self._prefix = prefix

    def _cmd(self, command, *args):
        if self._player_id is not None:
            args = (self._player_id,) + args
        args = ','.join(str(arg) for arg in args)
        return '%s.%s(%s)' % (self._prefix, command, args)

    def _get_pos(self):
        return Vector.from_string(
            self._connection.transact(self._cmd('getPos')), type=float)
    def _set_pos(self, value):
        self._connection.send(
            self._cmd('setPos', value.x, value.y, value.z))
    pos = property(_get_pos, _set_pos, doc="""\
        The precise position of the player within the world.

        This property returns the position of the selected player within the
        Minecraft world, as a :class:`~picraft.vector.Vector` instance. This is
        the *precise* position of the player including decimal places
        (representing portions of a tile). You can assign to this property to
        reposition the player.
        """)

    def _get_tile_pos(self):
        return Vector.from_string(
            self._connection.transact(self._cmd('getTile')))
    def _set_tile_pos(self, value):
        self._connection.send(
            self._cmd('setTile', value.x, value.y, value.z))
    tile_pos = property(_get_tile_pos, _set_tile_pos, doc="""\
        The position of the player within the world to the nearest block.

        This property returns the position of the selected player in the
        Minecraft world to the nearest block, as a
        :class:`~picraft.vector.Vector` instance.  You can assign to this
        property to reposition the player.
        """)

    @property
    def heading(self):
        """
        The direction the player is facing in clockwise degrees from South.

        This property can be queried to determine the direction that the player
        is facing. The value is returned as a floating-point number of degrees
        from North (i.e. 180 is North, 270 is East, 0 is South, and 90 is
        West).

        .. warning::

            Player heading is only *fully* supported on Raspberry Juice. On
            Minecraft Pi, it can be emulated by activating tracking for the
            player (see :attr:`~picraft.events.Events.track_players`) and
            periodically calling :meth:`~picraft.events.Events.poll`. However,
            this will only tell you what heading the player *moved* along, not
            necessarily what direction they're facing.
        """
        if self._connection.server_version == 'raspberry-juice':
            return float(
                self._connection.transact(self._cmd('getRotation')))
        else:
            pid = 1 if self._player_id is None else self._player_id
            try:
                d = self._connection._directions[pid].replace(y=0)
            except KeyError:
                raise NotSupported(
                    'cannot query heading on server version: %s or player '
                    'id %d is not currently tracked' %
                    (self._connection.server_version, pid))
            else:
                result = d.angle_between(Z)
                # |d×Z|=|d||Z|sin(t), ergo if y-component of d×Z is negative,
                # the result is >180
                if d.cross(Z).y < 0:
                    result += 180
                return result

    @property
    def pitch(self):
        """
        The elevation of the player's view in degrees from the horizontal.

        This property can be queried to determine whether the player is looking
        up (values from 0 to -90) or down (values from 0 down to 90). The value
        is returned as floating-point number of degrees from the horizontal.

        .. warning::

            Player pitch is only supported on Raspberry Juice.
        """
        if self._connection.server_version != 'raspberry-juice':
            raise NotSupported(
                'cannot query pitch on server version: %s' %
                self._connection.server_version)
        return float(
            self._connection.transact(self._cmd('getPitch')))

    @property
    def direction(self):
        """
        The direction the player is facing as a unit vector.

        This property can be queried to retrieve a unit
        :class:`~picraft.vector.Vector` pointing in the direction of the
        player's view.

        .. warning::

            Player direction is only *fully* supported on Raspberry Juice. On
            Minecraft Pi, it can be emulated by activating tracking for the
            player (see :attr:`~picraft.events.Events.track_players`) and
            periodically calling :meth:`~picraft.events.Events.poll`. However,
            this will only tell you what direction the player *moved* in, not
            necessarily what direction they're facing.
        """
        if self._connection.server_version == 'raspberry-juice':
            return Vector.from_string(
                self._connection.transact(self._cmd('getDirection')),
                type=float)
        else:
            pid = 1 if self._player_id is None else self._player_id
            try:
                return self._connection._directions[pid].unit
            except KeyError:
                raise NotSupported(
                    'cannot query direction on server version: %s or player '
                    'id %d is not currently tracked' %
                    (self._connection.server_version, pid))


class Player(BasePlayer):
    """
    Represents a player within the game world.

    Players are uniquely identified by their *player_id*. Instances of this
    class are available from the :attr:`~picraft.world.World.players` mapping.
    It provides properties to query and manipulate the position and settings of
    the player.
    """

    def __init__(self, connection, player_id):
        super(Player, self).__init__(connection, 'entity', player_id)

    def __repr__(self):
        return '<Player player_id=%d>' % self._player_id

    @property
    def player_id(self):
        """
        Returns the integer ID of the player on the server.
        """
        return self._player_id



class HostPlayer(BasePlayer):
    """
    Represents the host player within the game world.

    An instance of this class is accessible as the :attr:`Game.player`
    attribute. It provides properties to query and manipulate the position
    and settings of the host player.
    """

    def __init__(self, connection):
        super(HostPlayer, self).__init__(connection, 'player', None)

    def __repr__(self):
        return '<HostPlayer>'

    def _get_autojump(self):
        raise AttributeError(
                'reading autojump is not supported by the server')
    def _set_autojump(self, value):
        if self._connection.server_version != 'minecraft-pi':
            raise NotSupported(
                'cannot change player settings on server version: %s' %
                self._connection.server_version)
        self._connection.send('player.setting(autojump,%d)' % bool(value))
    autojump = property(_get_autojump, _set_autojump, doc="""\
        Write-only property which sets whether the host player autojumps.

        When this property is set to True (which is the default), the host
        player will automatically jump onto blocks when it runs into them
        (unless the blocks are too high to jump onto).

        .. warning::

            Player settings are only supported on Minecraft Pi edition.

        .. note::

            Unfortunately, the underlying protocol provides no means of reading
            a world setting, so this property is write-only (attempting to
            query it will result in an :exc:`AttributeError` being raised).
        """)

