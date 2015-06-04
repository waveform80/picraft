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

    .. attribute:: pos

        A :class:`~picraft.vector.Vector` indicating the position of the block
        which was struck.

    .. attribute:: face

        A string indicating which face of the block was struck. This can be one
        of six values: 'north', 'south', 'east', 'west', 'top', or 'bottom'.
        The 'north' and 'south' values corresponding to increasing and
        decreasing values along the Z axis; the 'east' and 'west' values to
        increasing and deceasing values along the X axis. Finally, 'top' and
        'bottom' refer to increasing and decreasing values along the Y axis.

    .. attribute:: player

        A :class:`~picraft.player.Player` instance representing the player that
        hit the block.
    """

    @classmethod
    def from_string(cls, connection, s):
        return cls(pos, face, Player(connection, int(player_id)))
