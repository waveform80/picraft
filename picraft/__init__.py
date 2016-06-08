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
The picraft package consists of several modules which permit access to and
modification of a Minecraft world. The package is intended as an alternative
Python API to the "official" Minecraft Python API (for reasons explained in the
:ref:`faq`).

The classes defined in most modules of this package are available directly
from the :mod:`picraft` namespace. In other words, the following code is
typically all that is required to access classes in this package::

    import picraft

For convenience on the command line you may prefer to simply do the following::

    from picraft import *

However, this is frowned upon in code as it pulls everything into the global
namespace, so you may prefer to do something like this::

    from picraft import World, Vector, Block

This is the style used in the :ref:`recipes` chapter. Sometimes, if you are
using the :class:`~picraft.vector.Vector` class extensively, you may wish to
use the short-cuts for it::

    from picraft import World, V, O, X, Y, Z, Block

The following sections document the various modules available within the
package:

* :ref:`api_world`
* :ref:`api_block`
* :ref:`api_vector`
* :ref:`api_events`
* :ref:`api_connection`
* :ref:`api_player`
* :ref:`api_exc`
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )

# Make Py2's str equivalent to Py3's
str = type('')


from .exc import (
    Error,
    ConnectionError,
    CommandError,
    NoResponse,
    BatchStarted,
    BatchNotStarted,
    NotSupported,
    ConnectionClosed,
    EmptySliceWarning,
    ParseWarning,
    UnsupportedCommand,
    NegativeWeight,
    )
from .vector import Vector, vector_range, line, lines, circle, sphere, filled, V, O, X, Y, Z
from .block import Block
from .events import BlockHitEvent, PlayerPosEvent, IdleEvent, ChatPostEvent
from .connection import Connection
from .player import Players, Player, HostPlayer
from .world import World
from .render import Model

