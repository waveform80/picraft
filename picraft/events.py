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

"""
The events module defines the :class:`Events` class, which provides methods for
querying events in the Minecraft world, and :class:`BlockHitEvent` which is the
only event type currently supported.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.events` directly.

The following items are defined in the module:


Events
======

.. autoclass:: Events
    :members:


BlockHitEvent
=============

.. autoclass:: BlockHitEvent(pos, face, player)
    :members:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from collections import namedtuple

from .vector import Vector
from .player import Player


class BlockHitEvent(namedtuple('BlockHitEvent', ('pos', 'face', 'player'))):
    """
    Event representing a block being hit by a player.

    This tuple derivative represents the event resulting from a player striking
    a block with their sword in the Minecraft world. Users will not normally
    need to construct instances of this class, rather they are constructed and
    returned by calls to :meth:`~Events.poll`.

    .. note::

        Please note that the block hit event only registers when the player
        *right clicks* with the sword. For some reason, left clicks do not
        count.

    .. attribute:: pos

        A :class:`~picraft.vector.Vector` indicating the position of the block
        which was struck.

    .. attribute:: face

        A string indicating which side of the block was struck. This can be one
        of six values: 'x+', 'x-', 'y+', 'y-', 'z+', or 'z-'. The value
        indicates the axis, and direction along that axis, that the side faces:

        .. image:: block_faces.png

    .. attribute:: player

        A :class:`~picraft.player.Player` instance representing the player that
        hit the block.
    """

    @classmethod
    def from_string(cls, connection, s):
        v, f, p = s.rsplit(',', 2)
        return cls(Vector.from_string(v), {
            0: 'y-',
            1: 'y+',
            2: 'z-',
            3: 'z+',
            4: 'x-',
            5: 'x+',
            }[int(f)], Player(connection, int(p)))

    def __repr__(self):
        return '<BlockHitEvent pos=%s face=%r player=%d>' % (
                self.pos, self.face, self.player.player_id)


class Events(object):
    """
    This class implements the :attr:`~picraft.world.World.events` attribute.
    """

    def __init__(self, connection):
        self._connection = connection

    def clear(self):
        """
        Forget all pending events that have not yet been retrieved with
        :meth:`poll`.

        This method is used to clear the list of block-hit events that have
        occurred since the last call to :meth:`poll` with retrieving them. This
        is useful for ensuring that events subsequently retrieved definitely
        occurred *after* the call to :meth:`clear`.
        """
        self._connection.send('events.clear()')

    def poll(self):
        """
        Return a list of all events that have occurred since the last call to
        :meth:`poll`. Currently the only type of event supported is the
        block-hit event represented by instances of :class:`BlockHitEvent`.

        For example::

            >>> w = World()
            >>> w.events.poll()
            [<BlockHit pos=1,1,1 face="x+" player=1>,
             <BlockHit pos=1,1,1 face="x+" player=1>]
        """
        events = self._connection.transact('events.block.hits()')
        if events:
            return [
                BlockHitEvent.from_string(self._connection, event)
                for event in events.split('|')
                ]
        return []

