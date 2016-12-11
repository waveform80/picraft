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
The events module defines the :class:`Events` class, which provides methods for
querying events in the Minecraft world, and the :class:`BlockHitEvent`,
:class:`PlayerPosEvent`, :class:`ChatPostEvent`, and :class:`IdleEvent` classes
which represent the various event types.

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


ChatPostEvent
=============

.. autoclass:: ChatPostEvent(message, player)
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
import warnings
from collections import namedtuple, Container
from weakref import WeakSet
from functools import update_wrapper
from types import FunctionType

from .exc import ConnectionClosed, NoHandlersWarning
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

        .. image:: images/block_faces.*

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


class ChatPostEvent(namedtuple('ChatPostEvent', ('message', 'player'))):
    """
    Event representing a chat post.

    This tuple derivative represents the event resulting from a chat message
    being posted in the Minecraft world. Users will not normally need to
    construct instances of this class, rather they are constructed and returned
    by calls to :meth:`~Events.poll`.

    .. note::

        Chat events are only generated by the Raspberry Juice server, not by
        Minecraft Pi edition.

    .. attribute:: message

        The message that was posted to the world.

    .. attribute:: player

        A :class:`~picraft.player.Player` instance representing the player that
        moved.
    """

    @classmethod
    def from_string(cls, connection, s):
        p, m = s.split(',', 1)
        return cls(m, Player(connection, int(p)))

    @property
    def __dict__(self):
        # Ensure __dict__ property works in Python 3.3 and above.
        return super(ChatPostEvent, self).__dict__

    def __repr__(self):
        return '<ChatPostEvent message=%s player=%d>' % (
                self.message, self.player.player_id)


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

    .. note::

        If you are using a Raspberry Juice server, chat post events are also
        tracked by default. Chat post events are only supported with Raspberry
        Juice servers; Minecraft Pi edition doesn't support chat post events.

    Finally, the :attr:`poll_gap` attribute specifies how long to pause during
    each iteration of :meth:`main_loop` to permit event handlers some time to
    interact with the server. Setting this to 0 will provide the fastest
    response to events, but will result in event handlers having to fight with
    event polling for access to the server.
    """

    def __init__(self, connection, poll_gap=0.1, include_idle=False):
        self._connection = connection
        self._handlers = []
        self._handler_instances = WeakSet()
        self._poll_gap = poll_gap
        self._include_idle = include_idle
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
                value: Player(self._connection, value).pos.round(1)
                }
        if self._connection.server_version != 'raspberry-juice':
            # Filter out calculated directions for untracked players
            self._connection._directions = {
                pid: delta
                for (pid, delta) in self._connection._directions.items()
                if pid in self._track_players
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
                    if self._connection.server_version != 'raspberry-juice':
                        # Calculate directions for tracked players on platforms
                        # which don't provide it natively
                        self._connection._directions[pid] = new_pos - old_pos
                    yield PlayerPosEvent(old_pos, new_pos, player)
                positions[pid] = new_pos

        def block_hit_events():
            s = self._connection.transact('events.block.hits()')
            if s:
                for e in s.split('|'):
                    yield BlockHitEvent.from_string(self._connection, e)

        def chat_post_events():
            if self._connection.server_version == 'raspberry-juice':
                s = self._connection.transact('events.chat.posts()')
                if s:
                    for e in s.split('|'):
                        yield ChatPostEvent.from_string(self._connection, e)

        events = list(player_pos_events(self._track_players)) + list(block_hit_events()) + list(chat_post_events())

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
        :meth:`main_loop`; developers should only call this method when
        implementing their own event loop manually, or when their (presumably
        non-threaded) event handler is engaged in a long operation and they
        wish to permit events to be processed in the meantime.
        """
        for event in self.poll():
            for handler in self._handlers:
                if handler.matches(event):
                    handler.execute(event)

    def has_handlers(self, cls):
        """
        Decorator for registering a class as containing picraft event handlers.

        If you are writing a class which contains methods that you wish to
        use as event handlers for picraft events, you must decorate the class
        with ``@has_handlers``. This will ensure that picraft tracks instances
        of the class and dispatches events to each instance that exists when
        the event occurs.

        For example::

            from picraft import World, Block, Vector, X, Y, Z

            world = World()

            @world.events.has_handlers
            class HitMe(object):
                def __init__(self, pos):
                    self.pos = pos
                    self.been_hit = False
                    world.blocks[self.pos] = Block('diamond_block')

                @world.events.on_block_hit()
                def was_i_hit(self, event):
                    if event.pos == self.pos:
                        self.been_hit = True
                        print('Block at %s was hit' % str(self.pos))

            p = world.player.tile_pos
            block1 = HitMe(p + 2*X)
            block2 = HitMe(p + 2*Z)
            world.events.main_loop()

        Class-based handlers are an advanced feature and have some notable
        limitations. For instance, in the example above the ``on_block_hit``
        handler couldn't be declared with the block's position because this was
        only known at instance creation time, not at class creation time (which
        was when the handler was registered).

        Furthermore, class-based handlers must be regular instance methods
        (those which accept the instance, self, as the first argument); they
        cannot be class methods or static methods.

        .. note::

            The ``@has_handlers`` decorator takes no arguments and shouldn't
            be called, unlike event handler decorators.
        """
        # Search the class for handler methods, appending the class to the
        # handler's list of associated classes (if you're thinking why is this
        # a collection, consider that a method can be associated with multiple
        # classes either by inheritance or direct assignment)
        handlers_found = 0
        for item in dir(cls):
            item = getattr(cls, item, None)
            if item: # PY2
                item = getattr(item, 'im_func', item)
            if item and isinstance(item, FunctionType):
                try:
                    item._picraft_classes.add(cls)
                    handlers_found += 1
                except AttributeError:
                    pass
        if not handlers_found:
            warnings.warn(NoHandlersWarning('no handlers found in %s' % cls))
            return cls
        # Replace __init__ on the class with a closure that adds every instance
        # constructed to self._handler_instances. As this is a WeakSet,
        # instances that die will be implicitly removed
        old_init = getattr(cls, '__init__', None)
        def __init__(this, *args, **kwargs):
            if old_init:
                old_init(this, *args, **kwargs)
            self._handler_instances.add(this)
        if old_init:
            update_wrapper(__init__, old_init)
        cls.__init__ = __init__
        return cls

    def _handler_closure(self, f):
        def handler(event):
            if not f._picraft_classes:
                # The handler is a straight-forward function; just call it
                f(event)
            else:
                # The handler is an unbound method (yes, I know these don't
                # really exist in Python 3; it's a function which is expecting
                # to be called from an object instance if you like). Here we
                # search the set of instances of classes which were registered
                # as having handlers (by @has_handlers)
                for cls in f._picraft_classes:
                    for inst in self._handler_instances:
                        # Check whether the instance has the right class; note
                        # that we *don't* use isinstance() here as we want an
                        # exact match
                        if inst.__class__ == cls:
                            # Bind the function to the instance via its
                            # descriptor
                            f.__get__(inst, cls)(event)
        update_wrapper(handler, f)
        return handler

    def on_idle(self, thread=False, multi=True):
        """
        Decorator for registering a function/method as an idle handler.

        This decorator is used to mark a function as an event handler which
        will be called when no other event handlers have been called in an
        iteration of :meth:`main_loop`. The function will be called with the
        corresponding :class:`IdleEvent` as the only argument.

        Note that idle events will only be generated if :attr:`include_idle`
        is set to ``True``.
        """
        def decorator(f):
            self._handlers.append(
                    IdleHandler(self._handler_closure(f), thread, multi))
            f._picraft_classes = set()
            return f
        return decorator

    def on_player_pos(self, thread=False, multi=True, old_pos=None, new_pos=None):
        """
        Decorator for registering a function/method as a position change
        handler.

        This decorator is used to mark a function as an event handler which
        will be called for any events indicating that a player's position has
        changed while :meth:`main_loop` is executing. The function will be
        called with the corresponding :class:`PlayerPosEvent` as the only
        argument.

        The *old_pos* and *new_pos* parameters can be used to specify vectors
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

            world.events.main_loop()

        Various effects can be achieved by combining *old_pos* and *new_pos*
        filters. For example, one could detect when a player crosses a boundary
        in a particular direction, or decide when a player enters or leaves a
        particular area.

        Note that only players specified in :attr:`track_players` will generate
        player position events.
        """
        def decorator(f):
            self._handlers.append(
                    PlayerPosHandler(self._handler_closure(f),
                        thread, multi, old_pos, new_pos))
            f._picraft_classes = set()
            return f
        return decorator

    def on_block_hit(self, thread=False, multi=True, pos=None, face=None):
        """
        Decorator for registering a function/method as a block hit handler.

        This decorator is used to mark a function as an event handler which
        will be called for any events indicating a block has been hit while
        :meth:`main_loop` is executing. The function will be called with the
        corresponding :class:`BlockHitEvent` as the only argument.

        The *pos* parameter can be used to specify a vector or sequence of
        vectors (including a :class:`~picraft.vector.vector_range`); in this
        case the event handler will only be called for block hits on matching
        vectors.

        The *face* parameter can be used to specify a face or sequence of
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

            world.events.main_loop()

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
            self._handlers.append(
                    BlockHitHandler(self._handler_closure(f),
                        thread, multi, pos, face))
            f._picraft_classes = set()
            return f
        return decorator

    def on_chat_post(self, thread=False, multi=True, message=None):
        """
        Decorator for registering a function/method as a chat event handler.

        This decorator is used to mark a function as an event handler which
        will be called for events indicating a chat message was posted to
        the world while :meth:`main_loop` is executing. The function will be
        called with the corresponding :class:`ChatPostEvent` as the only
        argument.

        .. note::

            Only the Raspberry Juice server generates chat events; Minecraft
            Pi Edition does not support this event type.

        The *message* parameter can be used to specify a string or regular
        expression; in this case the event handler will only be called for chat
        messages which match this value. For example::

            import re
            from picraft import World, Vector

            world = World()

            @world.events.on_chat_post(message="hello world")
            def echo(event):
                world.say("Hello player %d!" % event.player.player_id)

            @world.events.on_chat_post(message=re.compile(r"teleport_me \d+,\d+,\d+"))
            def teleport(event):
                x, y, z = event.message[len("teleport_me "):].split(",")
                event.player.pos = Vector(int(x), int(y), int(z))

            world.events.main_loop()

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
            self._handlers.append(
                    ChatPostHandler(self._handler_closure(f),
                        thread, multi, message))
            f._picraft_classes = set()
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
                threading.Thread(target=self._execute_handler, args=(event,)).start()
            elif not self._thread:
                self._thread = threading.Thread(target=self._execute_single, args=(event,))
                self._thread.start()
        else:
            self._execute_handler(event)

    def _execute_single(self, event):
        try:
            self._execute_handler(event)
        finally:
            self._thread = None

    def _execute_handler(self, event):
        self.action(event)

    def matches(self, event):
        """
        Tests whether or not *event* match all the filters for the handler that
        this object represents.
        """
        raise NotImplementedError


class PlayerPosHandler(EventHandler):
    """
    This class associates a handler with a player-position event.

    Constructor parameters are similar to the parent class,
    :class:`EventHandler` but additionally include *old_pos* and *new_pos* to
    specify the vectors (or sequences of vectors) that an event must transition
    across in order to activate this action. These filters must both match in
    order for the action to fire.
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
        raise TypeError(
                "%r is not a valid position test; expected Vector or "
                "sequence of Vector" % test)


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
        raise TypeError(
                "%r is not a valid position test; expected Vector or "
                "sequence of Vector" % pos)

    def matches_face(self, face):
        if self.face is None:
            return True
        if isinstance(self.face, str):
            return self.face == face
        if isinstance(self.face, Container):
            return face in self.face
        raise TypeError(
                "%r is not a valid face test; expected string or sequence "
                "of strings" % face)


class ChatPostHandler(EventHandler):
    """
    This class associates a handler with a chat-post event.

    Constructor parameters are similar to the parent class,
    :class:`EventHandler` but additionally include *message* to specify the
    message that an event must contain in order to activate this action.
    """

    def __init__(self, action, thread, multi, message):
        super(ChatPostHandler, self).__init__(action, thread, multi)
        if isinstance(message, bytes):
            message = message.decode('ascii')
        self.message = message

    def matches(self, event):
        return (
            isinstance(event, ChatPostEvent) and
            self.matches_message(event.message))

    def matches_message(self, message):
        if self.message is None:
            return True
        if isinstance(self.message, str):
            return self.message == message
        try:
            return self.message.match(message)
        except AttributeError:
            raise TypeError(
                    "%r is not a valid message test; expected string"
                    "or regular expression" % message)


class IdleHandler(EventHandler):
    """
    This class associates a handler with an idle event.
    """

    def matches(self, event):
        return isinstance(event, IdleEvent)
