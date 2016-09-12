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

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from threading import Lock, local
from collections import namedtuple

from .world import World
from .vector import Vector, O, X, Y, Z, vector_range, line
from .block import Block


class TurtleCache(object):
    """
    A representation of the world's blocks with implicit, thread-safe caching.

    Using the cache as a context manager starts a batch operation which builds
    up state changes until the termination of the ``with`` block. If the block
    is terminated without an exception being raised, all changes are applied
    to the world.

    Requesting the state of blocks will always read from the cache and, if
    a batch is active, from the (as yet uncommitted) changes made by the batch.
    Note that batches are stored in thread-local state.
    """
    def __init__(self, world):
        self._world = world
        self._lock = Lock()
        self._cache = {}
        self._batch = local()

    def __enter__(self):
        try:
            self._batch.level += 1
        except AttributeError:
            self._batch.level = 1
            self._batch.state = {}
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._batch.level -= 1
        if self._batch.level == 0:
            state = self._batch.state
            del self._batch.level, self._batch.state
            if exc_type is None:
                self.__setitem__(state.keys(), state.values())

    def __getitem__(self, positions):
        try:
            # no need for thread lock, as we're getting a thread local
            batch = self._batch.state
        except AttributeError:
            batch = {} # no active batch
        with self._lock:
            unknown = set(positions) - set(self._cache.keys()) - set(batch.keys())
            if unknown:
                self._cache.update({
                    v: b
                    for v, b in zip(unknown, self._world.blocks[unknown])
                    })
            return {
                v: batch.get(v, self._cache[v])
                for v in positions
                }

    def __setitem__(self, positions, blocks):
        try:
            # no need for thread lock, as we're updating a thread local
            self._batch.state.update({v: b for (v, b) in zip(positions, blocks)})
        except AttributeError:
            with self._lock:
                diff = {
                    v: b
                    for v, b in zip(positions, blocks)
                    if b != self._cache[v]
                    }
                with self._world.connection.batch_start():
                    self._world.blocks[diff.keys()] = diff.values()
                self._cache.update(diff)


class TurtleScreen(object):
    def __init__(self, world=None):
        if world is None:
            world = _default_world()
        self._world = world
        self._blocks = TurtleCache(world)

    @property
    def world(self):
        return self._world

    @property
    def blocks(self):
        return self._blocks

    def draw(self, state):
        self.blocks[state.keys()] = state.values()

    def chat(self, message):
        self._world.say(message)


TurtleState = namedtuple('TurtleState', (
    'position',  # Vector
    'heading',   # Vector
    'elevation', # angle (-90..90)
    'visible',   # bool
    'pendown',   # bool
    'penblock',  # Block
    'fillblock', # Block
    'changed',   # Vector->Block map
    'action',    # home/move/turtle
    ))


class Turtle(object):
    def __init__(self, screen=None, pos=None):
        if screen is None:
            screen = _default_screen()
        if pos is None:
            pos = screen.world.player.tile_pos - Y
        self._screen = screen
        self._state = TurtleState(
            position=pos,
            heading=Z,
            elevation=0.0,
            visible=True,
            pendown=True,
            penblock=Block('stone'),
            fillblock=Block('stone'),
            changed={},
            action='home',
            )
        self._last_position = self._state.position
        self._history = [self._state] # undo buffer
        self._draw_turtle()

    def _commit(self, changes, action):
        self._history.append(self._state._replace(
            changed=self._screen.blocks[changes.keys()], # reverse diff
            action=action
            ))
        if changes:
            self._screen.draw(changes)

    def _draw_vectors(self):
        arm_v = self._state.heading.cross(Y).unit
        if arm_v == O:
            arm_v = X
        head_v = self._state.heading.rotate(self._state.elevation, about=arm_v)
        return arm_v, head_v

    def _draw_turtle(self):
        arm_v, head_v = self._draw_vectors()
        head = (self._state.position + head_v).round()
        left_arm = (self._state.position + arm_v).round()
        right_arm = (self._state.position - arm_v).round()
        state = {
            v: Block('wool', 15)
            for v in (head, left_arm, right_arm)
            }
        if self._state.pendown:
            state[self._state.position] = self._state.penblock
        self._commit(state, 'turtle')

    def _undraw_turtle(self):
        with self._screen.blocks:
            while self._history and self._history[-1].action == 'turtle':
                self._screen.draw(self._history.pop().changed)

    def _update(self):
        with self._screen.blocks:
            self._undraw_turtle()
            if self._state.pendown and self._state.position != self._last_position:
                self._commit({
                    v: self._state.penblock
                    for v in line(self._last_position, self._state.position)
                    }, 'line')
            else:
                self._commit({}, 'move')
            if self._state.visible:
                self._draw_turtle()
            self._last_position = self._state.position

    def undo(self):
        with self._screen.blocks:
            self._undraw_turtle()
            if self._history[-1].action != 'home':
                self._screen.draw(self._history.pop().changed)
                self._state = self._history[-1]
                self._last_position = self._state.position
            if self._state.visible:
                self._draw_turtle()

    def home(self):
        self._state = self._state._replace(
            position=self._history[0].position,
            heading=Z,
            elevation=0.0,
            )
        self._update()

    def clear(self):
        with self._screen.blocks:
            while self._history[-1].action != 'home':
                self._screen.draw(self._history.pop().changed)
            self._update()

    def reset(self):
        with self._screen.blocks:
            self.clear()
            self._last_position = self._history[0].position
            self.home()

    def pos(self):
        return self._state.position

    def xcor(self):
        return self._state.position.x

    def ycor(self):
        return self._state.position.y

    def zcor(self):
        return self._state.position.z

    def goto(self, x, y=None, z=None):
        if isinstance(x, Turtle):
            other = x.pos()
        else:
            try:
                x, y, z = x
            except (TypeError, ValueError) as exc:
                pass
            other = Vector(x, y, z)
        self._state = self._state._replace(position=other)
        self._update()

    def distance(self, x, y=None, z=None):
        if isinstance(x, Turtle):
            other = x.pos()
        else:
            try:
                x, y, z = x
            except (TypeError, ValueError) as exc:
                pass
            other = Vector(x, y, z)
        return self._state.position.distance_to(other)

    def elevation(self):
        return self._state.elevation

    def heading(self):
        result = self._state.heading.angle_between(Z)
        if self._state.heading.cross(Z).y < 0:
            result += 180
        return result

    def setelevation(self, to_angle):
        self._state = self._state._replace(elevation=to_angle)
        self._update()

    def setheading(self, to_angle):
        self._state = self._state._replace(heading=Z.rotate(to_angle, about=Y))
        self._update()

    def forward(self, distance):
        arm_v, head_v = self._draw_vectors()
        self._state = self._state._replace(
            position=(self._state.position + distance * head_v).round()
            )
        self._update()

    def backward(self, distance):
        arm_v, head_v = self._draw_vectors()
        self._state = self._state._replace(
            position=(self._state.position - distance * head_v).round()
            )
        self._update()

    def right(self, angle):
        self._state = self._state._replace(
            heading=self._state.heading.rotate(-angle, about=Y)
            )
        self._update()

    def left(self, angle):
        self._state = self._state._replace(
            heading=self._state.heading.rotate(angle, about=Y)
            )
        self._update()

    def down(self, angle):
        self._state = self._state._replace(
            elevation=self._state.elevation - angle
            )
        self._update()

    def up(self, angle):
        self._state = self._state._replace(
            elevation=self._state.elevation + angle
            )
        self._update()

    def isdown(self):
        return self._state.pendown

    def pendown(self):
        self._state = self._state._replace(pendown=True)
        self._update()

    def penup(self):
        self._state = self._state._replace(pendown=False)
        self._update()

    def isvisible(self):
        return self._state.visible

    def showturtle(self):
        self._state = self._state._replace(visible=True)
        self._update()

    def hideturtle(self):
        self._state = self._state._replace(visible=False)
        self._update()

    def block(self, *args):
        if not args:
            return self.penblock(), self.fillblock()
        else:
            self.penblock(*args)
            self.fillblock(*args)

    def penblock(self, *args):
        if not args:
            return self._state.penblock
        elif isinstance(args[0], Block):
            self._state.penblock = Block
        else:
            self._state.penblock = Block(*args)

    def fillblock(self, *args):
        if not args:
            return self._state.fillblock
        elif isinstance(args[0], Block):
            self._state.fillblock = Block
        else:
            self._state.fillblock = Block(*args)

    position = pos
    setpos = goto
    setposition = goto
    sete = setelevation
    seth = setheading
    fd = forward
    bk = backward
    back = backward
    rt = right
    lt = left
    st = showturtle
    ht = hideturtle
    pd = pendown
    pu = penup


class TurtlePlayer(object):
    def __init__(self, screen=None, player_id=None):
        if screen is None:
            screen = _default_screen()
        self._screen = screen
        if player_id is None:
            self._player = self._screen.world.player
        else:
            self._player = self._screen.world.players[player_id]

    def where(self):
        return self._player.pos

    def teleport(self, x, y=None, z=None):
        if isinstance(x, Turtle):
            other = x.pos() + Y
        else:
            try:
                x, y, z = x
            except (TypeError, ValueError) as exc:
                pass
            other = Vector(x, y, z)
        self._player.pos = other

    def jump(self, height=2):
        self.teleport(self._player.pos + height * Y)


# default objects constructed when the straight function interface is used

_WORLD = None # The global World() used by default
_SCREEN = None # The global TurtleScreen() used by default
_TURTLE = None # The global Turtle() used by default
_PLAYER = None # The global TurtlePlayer() used by default

def _default_world():
    global _WORLD
    if _WORLD is None:
        _WORLD = World()
    return _WORLD

def _default_screen():
    global _SCREEN
    if _SCREEN is None:
        _SCREEN = TurtleScreen()
    return _SCREEN

def _default_turtle():
    global _TURTLE
    if _TURTLE is None:
        _TURTLE = Turtle()
    return _TURTLE

def _default_player():
    global _PLAYER
    if _PLAYER is None:
        _PLAYER = TurtlePlayer()
    return _PLAYER

home = lambda: _default_turtle().home()
clear = lambda: _default_turtle().clear()
reset = lambda: _default_turtle().reset()
pos = lambda: _default_turtle().pos()
xcor = lambda: _default_turtle().xcor()
ycor = lambda: _default_turtle().ycor()
zcor = lambda: _default_turtle().zcor()
goto = lambda x, y=None, z=None: _default_turtle().goto(x, y, z)
distance = lambda x, y=None, z=None: _default_turtle().distance(x, y, z)
elevation = lambda: _default_turtle().elevation()
heading = lambda: _default_turtle().heading()
setelevation = lambda to_angle: _default_turtle().setelevation(to_angle)
setheading = lambda to_angle: _default_turtle().setheading(to_angle)
forward = lambda distance: _default_turtle().forward(distance)
backward = lambda distance: _default_turtle().backward(distance)
right = lambda angle: _default_turtle().right(angle)
left = lambda angle: _default_turtle().left(angle)
down = lambda angle: _default_turtle().down(angle)
up = lambda angle: _default_turtle(angle)
isdown = lambda: _default_turtle().isdown()
pendown = lambda: _default_turtle().pendown()
penup = lambda: _default_turtle().penup()
isvisible = lambda: _default_turtle().isvisible()
showturtle = lambda: _default_turtle().showturtle()
hideturtle = lambda: _default_turtle().hideturtle()
block = lambda *args: _default_turtle().block(*args)
penblock = lambda *args: _default_turtle().penblock(*args)
fillblock = lambda *args: _default_turtle().fillblock(*args)
undo = lambda: _default_turtle().undo()
position = pos
setpos = goto
setposition = goto
sete = setelevation
seth = setheading
fd = forward
bk = backward
back = backward
rt = right
lt = left
st = showturtle
ht = hideturtle
pd = pendown
pu = penup
where = lambda: _default_player().where()
teleport = lambda x, y=None, z=None: _default_player().teleport(x, y, z)
jump = lambda height=2: _default_player().jump(height)
chat = lambda message: _default_screen().chat(message)
