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


from threading import Lock

from .world import World
from .vector import Vector, O, X, Y, Z, vector_range, line
from .block import Block


_WORLD = None # The global World() used by default
_SCREEN = None # The global TurtleScreen() used by default
_TURTLE = None # The global Turtle() used by default


class TurtleScreen(object):
    def __init__(self, world=None):
        global _WORLD
        if world is None:
            if _WORLD is None:
                _WORLD = World()
            world = _WORLD
        self._world = world
        self._lock = Lock()
        self._original = {} # state of the world without any turtles / drawings
        self._current = {} # state of the world with drawings and turtles

    @property
    def lock(self):
        return self._lock

    @property
    def world(self):
        return self._world

    def original(self, around=None, radius=1):
        with self._lock:
            if around is None:
                return self._original.copy()
            else:
                was_empty = not self._original
                around = vector_range(around - radius, around + radius + 1)
                unknown = set(around) - set(self._original.keys())
                if unknown:
                    if self._world.connection.server_version == 'raspberry-juice':
                        # optimization: cost of getting a cuboid range of
                        # blocks is the same as that of getting a single block
                        # in raspberry juice
                        to_update = {
                            v: b
                            for v, b in zip(around, self._world.blocks[around])
                            if v not in self._original
                            }
                    else:
                        to_update = {
                            v: b
                            for v, b in zip(unknown, self._world.blocks[unknown])
                            }
                    self._original.update(to_update)
                    self._current.update(to_update)
                return {
                    v: self._original[v]
                    for v in around
                    }

    def update(self, state):
        with self._lock:
            missing = {
                v: self._world.blocks[v]
                for v in state
                if v not in self._original
                }
            self._original.update(missing)
            self._current.update(missing)
            d = {
                v: b
                for v, b in state.items()
                if b != self._current[v]
                }
            with self._world.connection.batch_start():
                self._world.blocks[d.keys()] = d.values()
            self._current.update(d)


class Turtle(object):
    def __init__(self, screen=None):
        global _SCREEN
        if screen is None:
            if _SCREEN is None:
                _SCREEN = TurtleScreen()
            screen = _SCREEN
        self._screen = screen
        self._home = self._screen.world.player.tile_pos - Y
        self._position = self._home
        self._last_position = self._position
        self._heading = Z # always a unit vector
        self._visible = True
        self._pendown = True
        self._penblock = Block('stone')
        self._fillblock = Block('stone')
        self._canvas = {} # blocks drawn by this turtle
        self._update()

    def _update(self):
        # original state of world (i.e. without the turtle)
        state = self._screen.original(around=self._last_position, radius=1)
        state.update(self._screen.original(around=self._position, radius=1))
        state.update(self._canvas)
        # calculate "after" state which is based upon canvas state
        if self._visible:
            head = (self._position + self._heading).round()
            arm_v = self._heading.cross(Y).unit
            if arm_v == O:
                arm_v = X
            left_arm = (self._position + arm_v).round()
            right_arm = (self._position - arm_v).round()
            b = Block('wool', 15)
            if self._pendown:
                for v in line(self._last_position, self._position):
                    self._canvas[v] = self._penblock
                    state[v] = self._penblock
            state[head] = b
            state[left_arm] = b
            state[right_arm] = b
        # calculate which blocks actually need changing and apply the minimal
        # set of changes
        self._screen.update(state)
        self._last_position = self._position

    def home(self):
        self._position = self._home
        self._heading = Z
        self._update()

    def clear(self):
        self._canvas = {}
        self._screen.update(self._screen.original())
        self._update()

    def reset(self):
        self.clear()
        self.home()

    def pos(self):
        return self._position

    def xcor(self):
        return self._position.x

    def ycor(self):
        return self._position.y

    def zcor(self):
        return self._position.z

    def goto(self, x, y=None, z=None):
        if isinstance(x, Turtle):
            other = x.pos()
        else:
            try:
                x, y, z = x
            except (TypeError, ValueError) as exc:
                pass
            other = Vector(x, y, z)
        self._position = other
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
        return self._position.distance_to(other)

    def heading(self):
        result = self._heading.angle_between(Z)
        if self._heading.cross(Z).y < 0:
            result += 180
        return result

    def setheading(self, to_angle):
        self._heading = Z.rotate(to_angle, about=Y)
        self._update()

    def forward(self, distance):
        self._position = (self._position + distance * self._heading).round()
        self._update()

    def backward(self, distance):
        self._position = (self._position - distance * self._heading).round()
        self._update()

    def right(self, angle):
        self._heading = self._heading.rotate(-angle, about=Y)
        self._update()

    def left(self, angle):
        self._heading = self._heading.rotate(angle, about=Y)
        self._update()

    def down(self, angle):
        pass

    def up(self, angle):
        pass

    def isdown(self):
        return self._pendown

    def pendown(self):
        self._pendown = True
        self._update()

    def penup(self):
        self._pendown = False
        self._update()

    def isvisible(self):
        return self._visible

    def showturtle(self):
        self._visible = True
        self._update()

    def hideturtle(self):
        self._visible = False
        self._update()

    def block(self, *args):
        if not args:
            return self.penblock(), self.fillblock()
        else:
            self.penblock(*args)
            self.fillblock(*args)

    def penblock(self, *args):
        if not args:
            return self._penblock
        elif isinstance(args[0], Block):
            self._penblock = Block
        else:
            self._penblock = Block(*args)

    def fillblock(self, *args):
        if not args:
            return self._fillblock
        elif isinstance(args[0], Block):
            self._fillblock = Block
        else:
            self._fillblock = Block(*args)

    position = pos
    setpos = goto
    setposition = goto
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



def _default_turtle():
    global _TURTLE
    if _TURTLE is None:
        _TURTLE = Turtle()
    return _TURTLE



