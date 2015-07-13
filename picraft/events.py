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


import logging
import threading
import time
from collections import namedtuple, Container

from .exc import ConnectionClosed
from .vector import Vector
from .player import Player

logger = logging.getLogger('picraft')


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

    @property
    def __dict__(self):
        # Ensure __dict__ property works in Python 3.3 and above.
        return super(BlockHitEvent, self).__dict__

    def __repr__(self):
        return '<BlockHitEvent pos=%s face=%r player=%d>' % (
                self.pos, self.face, self.player.player_id)


class Events(object):
    """
    This class implements the :attr:`~picraft.world.World.events` attribute.
    """

    def __init__(self, connection):
        self._connection = connection
        self._handlers = []
        self.poll_gap = 0.1

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

    def main_loop(self):
        """
        Starts the event polling loop when using the decorator style of event
        handling (see :meth:`block_hit`).

        This method will not return, so be sure that you have specified all
        your event handlers before calling it. The event loop can only be
        broken by an unhandled exception, or by closing the world's connection
        (in the latter case the resulting :exc:`~picraft.exc.ConnectionClosed`
        exception will be suppressed as it is assumed that you want to end the
        script cleanly).
        """
        logger.info('Entering event loop')
        try:
            while True:
                self.process()
                time.sleep(self.poll_gap)
        except ConnectionClosed:
            logger.info('Connection closed; exiting event loop')

    def process(self):
        """
        Poll the server for events and call any relevant event handlers
        registered with :meth:`block_hit`.

        This method is called repeatedly the event handler loop implemented by
        :meth:`main_loop`; developers should only call this method when their
        (presumably non-threaded) event handler is engaged in a long operation
        and they wish to permit events to be processed in the meantime.
        """
        for event in self.poll():
            for handler in self._handlers:
                if handler.matches(event):
                    handler.execute(event)

    def block_hit(self, pos=None, face=None, thread=False, multi=True):
        """
        Decorator for registering a function as an event handler.

        This decorator is used to mark a function as an event handler which
        will be called for any matching events while :meth:`main_loop` is
        executing. The decorator has two optional attributes which can be used
        to filter the events for which the handler will be called.

        The *pos* attribute can be used to specify a vector or sequence of
        vectors (including a :class:`~picraft.vector.vector_range`); in this
        case the event handler will only be called for block hits on matching
        vectors.

        The *face* attribute can be used to specify a face or sequence of
        faces for which the handler will be called.

        For example, to specify that one handler should be called for hits
        on the top of any blocks, and another should be called only for hits
        on any face of block at the origin one could use the following code::

            from picraft import World, Vector

            world = World()

            @world.events.block_hit(pos=Vector(0, 0, 0))
            def origin_hit(event):
                world.say('You hit the block at the origin')

            @world.events.block_hit(face="y+")
            def top_hit(event):
                world.say('You hit the top of a block at %d,%d,%d' % event.pos)

        The *thread* parameter (which defaults to ``False``) can be used to
        specify that the handler should be executed in its own background
        thread, in parallel with other handlers.

        Finally, the *multi* parameter (which only applies when *thread* is
        ``True``) specifies whether multi-threaded handlers should be allowed
        to execute in parallel. When ``True`` (the default), threaded handlers
        execute as many times as activated in parallel. When ``False``, a
        single instance of a threaded handler is allowed to execute at any
        given time; simultaneous activations are ignored (but not queued, as
        with unthreaded handlers).
        """
        def decorator(f):
            self._handlers.append(EventHandler(f, pos, face, thread, multi))
            return f
        return decorator


class EventHandler(object):
    """
    This is an internal object used to associate event handlers with their
    activation restrictions.

    The *action* parameter specifies the function to be run when a matching
    event is received from the server. The *pos* parameter specifies the
    vector (or sequence of vectors) which an event must match in order to
    activate this action. The *face* parameter specifies the block face (or
    set of faces) which an event must match in order to activate this action.
    These filters must both match in order for the action to fire.

    The *thread* parameter specifies whether the *action* will be launched in
    its own background thread. If *multi* is ``False``, then the
    :meth:`execute` method will ensure that any prior execution has finished
    before launching another one.
    """

    def __init__(self, action, pos, face, thread, multi):
        self.action = action
        self.pos = pos
        if isinstance(face, bytes):
            face = face.decode('ascii')
        self.face = face
        self.thread = thread
        self.multi = multi
        self._thread = None

    def execute(self, event):
        """
        Launches the *action* in a background thread if necessary. If required,
        this method also ensures threaded actions don't overlap.
        """
        if self.thread:
            if self.multi:
                threading.Thread(target=self.action, args=(event,)).start()
            elif not self._thread:
                self._thread = threading.Thread(target=self.execute_single, args=(event,))
                self._thread.start()
        else:
            self.action(event)

    def execute_single(self, event):
        try:
            self.action(event)
        finally:
            self._thread = None

    def matches(self, event):
        """
        Tests whether or not *event* match all the filters for the handler that
        this object represents.
        """
        return self.matches_pos(event.pos) and self.matches_face(event.face)

    def matches_pos(self, pos):
        if self.pos is None:
            return True
        if isinstance(self.pos, Vector):
            return self.pos == pos
        if isinstance(self.pos, Container):
            return pos in self.pos
        return False

    def matches_face(self, face):
        if self.face is None:
            return True
        if isinstance(self.face, str):
            return self.face == face
        if isinstance(self.face, Container):
            return face in self.face
        return False

