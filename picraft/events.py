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


PlayerPosEvent
==============

.. autoclass:: PlayerPosEvent(old_pos, new_pos, player)
    :members:


IdleEvent
=========

.. autoclass:: IdleEvent()
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


class PlayerPosEvent(namedtuple('PlayerPosEvent', ('old_pos', 'new_pos', 'player'))):
    """
    Event representing a player moving.

    This tuple derivative represents the event resulting from a player moving
    within the Minecraft world. Users will not normally need to construct
    instances of this class, rather they are constructed and returned by calls
    to :meth:`~Events.poll`.

    .. attribute:: old_pos

        A :class:`~picraft.vector.Vector` indicating the location of the player
        prior to this event. The location includes decimal places (it is not
        the tile-position, but the actual position).

    .. attribute:: new_pos

        A :class:`~picraft.vector.Vector` indicating the location of the player
        as of this event. The location includes decimal places (it is not
        the tile-position, but the actual position).

    .. attribute:: player

        A :class:`~picraft.player.Player` instance representing the player that
        moved.
    """

    @property
    def __dict__(self):
        # Ensure __dict__ property works in Python 3.3 and above.
        return super(PlayerPosEvent, self).__dict__

    def __repr__(self):
        return '<PlayerPosEvent old_pos=%s new_pos=%s player=%d>' % (
                self.old_pos, self.new_pos, self.player.player_id)


class IdleEvent(namedtuple('IdleEvent', ())):
    """
    Event that fires in the event that no other events have occurred since the
    last poll. This is only used if :attr:`Events.include_idle` is ``True``.
    """

    @property
    def __dict__(self):
        # Ensure __dict__ property works in Python 3.3 and above.
        return super(IdleEvent, self).__dict__

    def __repr__(self):
        return '<IdleEvent>'


class Events(object):
    """
    This class implements the :attr:`~picraft.world.World.events` attribute.

    There are two ways of responding to picraft's events: the first is to
    :meth:`poll` for them manually, and process each event in the resulting
    list::

        >>> for event in world.events.poll():
        ...     print(repr(event))
        ...
        <BlockHitEvent pos=1,1,1 face="y+" player=1>,
        <PlayerPosEvent old_pos=0.2,1.0,0.7 new_pos=0.3,1.0,0.7 player=1>

    The second is to "tag" functions as event handlers with the decorators
    provided and then call the :meth:`main_loop` function which will handle
    polling the server for you, and call all the relevant functions as needed::

        @world.events.on_block_hit(pos=Vector(1,1,1))
        def hit_block(event):
            print('You hit the block at %s' % event.pos)

        world.events.main_loop()

    By default, only block hit events will be tracked. This is because it is
    the only type of event that the Minecraft server provides information about
    itself, and thus the only type of event that can be processed relatively
    efficiently. If you wish to track player positions, assign a set of player
    ids to the :attr:`track_players` attribute. If you wish to include idle
    events (which fire when nothing else is produced in response to
    :meth:`poll`) then set :attr:`include_idle` to ``True``.

    Finally, the :attr:`poll_gap` attribute specifies how long to pause during
    each iteration of :meth:`main_loop` to permit event handlers some time to
    interact with the server. Setting this to 0 will provide the fastest
    response to events, but will result in event handlers having to fight with
    event polling for access to the server.
    """

    def __init__(self, connection):
        self._connection = connection
        self._handlers = []
        self._poll_gap = 0.1
        self._include_idle = False
        self._track_players = {}

    def _get_poll_gap(self):
        return self._poll_gap
    def _set_poll_gap(self, value):
        self._poll_gap = float(value)
    poll_gap = property(_get_poll_gap, _set_poll_gap, doc="""\
        The length of time (in seconds) to pause during :meth:`main_loop`.

        This property specifies the length of time to wait at the end of each
        iteration of :meth:`main_loop`. By default this is 0.1 seconds.

        The purpose of the pause is to give event handlers executing in the
        background time to communicate with the Minecraft server. Setting this
        to 0.0 will result in faster response to events, but also starves
        threaded event handlers of time to communicate with the server,
        resulting in "choppy" performance.
        """)

    def _get_track_players(self):
        return self._track_players.keys()
    def _set_track_players(self, value):
        try:
            self._track_players = {
                pid: Player(self._connection, pid).pos.round(1)
                for pid in value
                }
        except TypeError:
            if not isinstance(value, int):
                raise ValueError(
                        'track_players value must be a player id '
                        'or a sequence of player ids')
            self._track_players = {
                value: Player(self._connection, value).pos
                }
    track_players = property(_get_track_players, _set_track_players, doc="""\
        The set of player ids for which movement should be tracked.

        By default the :meth:`poll` method will not produce player position
        events (:class:`PlayerPosEvent`). Producing these events requires extra
        interactions with the Minecraft server (one for each player tracked)
        which slow down response to block hit events.

        If you wish to track player positions, set this attribute to the set of
        player ids you wish to track and their positions will be stored.  The
        next time :meth:`poll` is called it will query the positions for all
        specified players and fire player position events if they have changed.

        Given that the :attr:`~picraft.world.World.players` attribute
        represents a dictionary mapping player ids to players, if you wish to
        track all players you can simply do::

            >>> world.events.track_players = world.players
        """)

    def _get_include_idle(self):
        return self._include_idle
    def _set_include_idle(self, value):
        self._include_idle = bool(value)
    include_idle = property(_get_include_idle, _set_include_idle, doc="""\
        If ``True``, generate an idle event when no other events would be
        generated by :meth:`poll`. This attribute defaults to ``False``.
        """)

    def clear(self):
        """
        Forget all pending events that have not yet been retrieved with
        :meth:`poll`.

        This method is used to clear the list of events that have occurred
        since the last call to :meth:`poll` without retrieving them. This is
        useful for ensuring that events subsequently retrieved definitely
        occurred *after* the call to :meth:`clear`.
        """
        self._set_track_players(self._get_track_players())
        self._connection.send('events.clear()')

    def poll(self):
        """
        Return a list of all events that have occurred since the last call to
        :meth:`poll`.

        For example::

            >>> w = World()
            >>> w.events.track_players = w.players
            >>> w.events.include_idle = True
            >>> w.events.poll()
            [<PlayerPosEvent old_pos=0.2,1.0,0.7 new_pos=0.3,1.0,0.7 player=1>,
             <BlockHitEvent pos=1,1,1 face="x+" player=1>,
             <BlockHitEvent pos=1,1,1 face="x+" player=1>]
            >>> w.events.poll()
            [<IdleEvent>]
        """
        def player_pos_events(positions):
            for pid, old_pos in positions.items():
                player = Player(self._connection, pid)
                new_pos = player.pos.round(1)
                if old_pos != new_pos:
                    yield PlayerPosEvent(old_pos, new_pos, player)
                positions[pid] = new_pos

        def block_hit_events():
            s = self._connection.transact('events.block.hits()')
            if s:
                for e in s.split('|'):
                    yield BlockHitEvent.from_string(self._connection, e)

        events = list(player_pos_events(self._track_players)) + list(block_hit_events())

        if events:
            return events
        elif self._include_idle:
            return [IdleEvent()]
        else:
            return []

    def main_loop(self):
        """
        Starts the event polling loop when using the decorator style of event
        handling (see :meth:`on_block_hit`).

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
        registered with :meth:`on_block_hit`.

        This method is called repeatedly the event handler loop implemented by
        :meth:`main_loop`; developers should only call this method when their
        (presumably non-threaded) event handler is engaged in a long operation
        and they wish to permit events to be processed in the meantime.
        """
        for event in self.poll():
            for handler in self._handlers:
                if handler.matches(event):
                    handler.execute(event)

    def on_idle(self, thread=False, multi=True):
        """
        Decorator for registering a function as an idle handler.

        This decorator is used to mark a function as an event handler which
        will be called when no other event handlers have been called in an
        iteration of :meth:`main_loop`. The function will be called with the
        corresponding :class:`IdleEvent` as the only argument.

        Note that idle events will only be generated if :attr:`include_idle`
        is set to ``True``.
        """
        def decorator(f):
            self._handlers.append(IdleHandler(f, thread, multi))
            return f
        return decorator

    def on_player_pos(self, thread=False, multi=True, old_pos=None, new_pos=None):
        """
        Decorator for registering a function as a position change handler.

        This decorator is used to mark a function as an event handler which
        will be called for any events indicating that a player's position has
        changed while :meth:`main_loop` is executing. The function will be
        called with the corresponding :class:`PlayerPosEvent` as the only
        argument.

        The *old_pos* and *new_pos* attributes can be used to specify vectors
        or sequences of vectors (including a
        :class:`~picraft.vector.vector_range`) that the player position events
        must match in order to activate the associated handler. For example, to
        fire a handler every time any player enters or walks over blocks within
        (-10, 0, -10) to (10, 0, 10)::

            from picraft import World, Vector, vector_range

            world = World()
            world.events.track_players = world.players

            from_pos = Vector(-10, 0, -10)
            to_pos = Vector(10, 0, 10)
            @world.events.on_player_pos(new_pos=vector_range(from_pos, to_pos + 1))
            def in_box(event):
                world.say('Player %d stepped in the box' % event.player.player_id)

        Various effects can be achieved by combining *old_pos* and *new_pos*
        filters. For example, one could detect when a player crosses a boundary
        in a particular direction, or decide when a player enters or leaves a
        particular area.

        Note that only players specified in :attr:`track_players` will generate
        player position events.
        """
        def decorator(f):
            self._handlers.append(PlayerPosHandler(f, thread, multi, old_pos, new_pos))
            return f
        return decorator

    def on_block_hit(self, thread=False, multi=True, pos=None, face=None):
        """
        Decorator for registering a function as an event handler.

        This decorator is used to mark a function as an event handler which
        will be called for any events indicating a block has been hit while
        :meth:`main_loop` is executing. The function will be called with the
        corresponding :class:`BlockHitEvent` as the only argument.

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

            @world.events.on_block_hit(pos=Vector(0, 0, 0))
            def origin_hit(event):
                world.say('You hit the block at the origin')

            @world.events.on_block_hit(face="y+")
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
            self._handlers.append(BlockHitHandler(f, thread, multi, pos, face))
            return f
        return decorator


class EventHandler(object):
    """
    This is an internal object used to associate event handlers with their
    activation restrictions.

    The *action* parameter specifies the function to be run when a matching
    event is received from the server.

    The *thread* parameter specifies whether the *action* will be launched in
    its own background thread. If *multi* is ``False``, then the
    :meth:`execute` method will ensure that any prior execution has finished
    before launching another one.
    """

    def __init__(self, action, thread, multi):
        self.action = action
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
        return False


class PlayerPosHandler(EventHandler):
    """
    This class associates a handler with a player-position event.

    Constructor parameters are similar to the parent class,
    :class:`EventHandler` but additionally include 
    """

    def __init__(self, action, thread, multi, old_pos, new_pos):
        super(PlayerPosHandler, self).__init__(action, thread, multi)
        self.old_pos = old_pos
        self.new_pos = new_pos

    def matches(self, event):
        return (
                isinstance(event, PlayerPosEvent) and
                self.matches_pos(self.old_pos, event.old_pos) and
                self.matches_pos(self.new_pos, event.new_pos))

    def matches_pos(self, test, pos):
        if test is None:
            return True
        if isinstance(test, Vector):
            return test == pos.floor()
        if isinstance(test, Container):
            return pos.floor() in test
        return False


class BlockHitHandler(EventHandler):
    """
    This class associates a handler with a block-hit event.

    Constructor parameters are similar to the parent class,
    :class:`EventHandler` but additionally include *pos* to specify the vector
    (or sequence of vectors) which an event must match in order to activate
    this action, and *face* to specify the block face (or set of faces) which
    an event must match.  These filters must both match in order for the action
    to fire.
    """

    def __init__(self, action, thread, multi, pos, face):
        super(BlockHitHandler, self).__init__(action, thread, multi)
        self.pos = pos
        if isinstance(face, bytes):
            face = face.decode('ascii')
        self.face = face

    def matches(self, event):
        return (
                isinstance(event, BlockHitEvent) and
                self.matches_pos(event.pos) and
                self.matches_face(event.face))

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


class IdleHandler(EventHandler):
    """
    This class associates a handler with an idle event.
    """

    def matches(self, event):
        return isinstance(event, IdleEvent)

