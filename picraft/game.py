# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# An alternate Python Minecraft lirbary for the Rasperry-Pi
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


import math
import socket
import logging
from collections import namedtuple


class PiCraftError(Exception):
    "Base class for all PiCraft exceptions"

class BatchError(PiCraftError):
    "Base class for PiCraft batch errors"

class BatchStarted(BatchError):
    "Exception raised when a batch is started before a prior one is complete"

class BatchNotStarted(BatchError):
    "Exception raised when a batch is terminated when none has been started"


class Vector(namedtuple('Vector', ('x', 'y', 'z'))):
    """
    Represents a 3-dimensional vector.

    This tuple derivative represents a 3-dimensional vector with x, y, z
    components. The class supports simple arithmetic operations with other
    vectors such as addition and subtraction, along with multiplication and
    division with scalars. Taking the absolute value of the vector will
    return its magnitude (according to `Pythagoras' theorem`_). For example::

        >>> v1 = Vector(1, 1, 1)
        >>> v2 = Vector(2, 2, 2)
        >>> v1 + v2
        Vector(3, 3, 3)
        >>> 2 * v2
        Vector(4, 4, 4)
        >>> abs(v1)
        1.0

    .. Pythagoras' theorem: https://en.wikipedia.org/wiki/Pythagorean_theorem

    .. note::

        Note that, as a derivative of tuple, instances of this class are
        immutable. That is, you cannot directly manipulate the x, y, and z
        attributes; instead you must create a new vector (for example, by
        adding two vectors together). The advantage of this is that vector
        instances can be used in sets or as dictionary keys.
    """

    def __new__(cls, x=0, y=0, z=0):
        return super(Vector, cls).__new__(cls, x, y, z)

    @classmethod
    def from_string(cls, s):
        x, y, z = s.split(',', 2)
        return cls(float(x), float(y), float(z))

    def __add__(self, other):
        try:
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        except AttributeError:
            return Vector(self.x + other, self.y + other, self.z + other)

    __radd__ = __add__

    def __sub__(self, other):
        try:
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        except AttributeError:
            return Vector(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        try:
            return Vector(self.x * other.x, self.y * other.y, self.z * other.z)
        except AttributeError:
            return Vector(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        try:
            return Vector(self.x / other.x, self.y / other.y, self.z / other.z)
        except AttributeError:
            return Vector(self.x / other, self.y / other, self.z / other)

    def __floordiv__(self, other):
        try:
            return Vector(self.x // other.x, self.y // other.y, self.z // other.z)
        except AttributeError:
            return Vector(self.x // other, self.y // other, self.z // other)

    def __mod__(self, other):
        try:
            return Vector(self.x % other.x, self.y % other.y, self.z % other.z)
        except AttributeError:
            return Vector(self.x % other, self.y % other, self.z % other)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __pos__(self):
        return self

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def __bool__(self):
        return self.x or self.y or self.z

    # Py2 compat
    __nonzero__ = __bool__
    __div__ = __truediv__

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x)

    def distance_to(self, other):
        return math.sqrt(
                (self.x - other.x) ** 2 +
                (self.y - other.y) ** 2 +
                (self.z - other.z) ** 2)

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @property
    def unit(self):
        if self.magnitude > 0:
            return self / self.magnitude
        else:
            return self


class Connection(object):
    """
    Represents the connection to the Minecraft server.

    The *host* parameter specifies the hostname or IP address of the Minecraft
    server, while the port specifies the port to connect to (these typically
    take the values "127.0.0.1" and 4711 respectively).

    Users will rarely need to construct a :class:`Connection` object
    themselves. An instance of this class is constructed by
    :class:`Game` to handle communication with the game server
    (:attr:`Game.connection`).

    The most important aspect of this class is its ability to "batch"
    transmissions together. Typically, the :meth:`send` method is used to
    transmit requests to the Minecraft server. When this is called normally
    (outside of a batch), it immediately transmits the requested data. However,
    if :meth:`batch_start` has been called first, the data is *not* sent
    immediately, but merely appended to the batch. The :meth:`batch_send`
    method can then be used to transmit all requests simultaneously (or
    alternatively, :meth:`batch_forget` can be used to discard the list). See
    the docs of these methods for more information.
    """
    encoding = 'ascii'

    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._rfile = self._socket.makefile('rb')
        self._wfile = self._socket.makefile('wb')
        self._batch = None

    def close(self):
        """
        Closes the connection.

        This method can be used to close down the connection to the game
        server. It is typically called from :meth:`Game.close` rather
        than being called directly.
        """
        try:
            self.batch_forget()
        except BatchNotStarted:
            pass
        if self._rfile:
            self._rfile.close()
            self._rfile = None
        if self._wfile:
            self._wfile.close()
            self._wfile = None
        if self._socket:
            self._socket.close()
            self._socket = None

    def _send(self, buf):
        if not isinstance(buf, bytes):
            buf = buf.encode(self.encoding)
        self._wfile.write(buf)
        logging.debug('picraft >: %r' % buf)

    def send(self, buf):
        """
        Transmits the contents of *buf* to the connected server.

        If no batch has been initiated (with :meth:`batch_start`), this method
        immediately communicates the contents of *buf* to the connected
        Minecraft server. If *buf* is a unicode string, the method attempts
        to encode the content in a byte-encoding prior to transmission (the
        encoding used is the :attr:`encoding` attribute of the class which
        defaults to "ascii").

        If a batch has been initiated, the contents of *buf* are appended to
        the latest batch that was started (batches can be nested; see
        :meth:`batch_start` for more information).
        """
        if self._batch is not None:
            self._batch.append(buf)
        else:
            self._send(buf)

    def transact(self, buf):
        """
        Transmits the contents of *buf*, and returns the reply string.

        This method immediately communicates the contents of *buf* to the
        connected server, then reads a line of data in reply and returns it.

        .. note::

            This method ignores the batch mechanism entirely as transmission
            is required in order to obtain the response. As this method
            is typically used to implement "getters", this is not usually an
            issue but it is worth bearing in mind.
        """
        self._send(buf)
        result = self._rfile.readline()
        logging.debug('picraft <: %r' % result)
        return result

    def batch_start(self):
        """
        Starts a new batch transmission.

        When called, this method starts a new batch transmission. All
        subsequent calls to :meth:`send` will append data to the batch buffer
        instead of actually sending the data.

        To terminate the batch transmission, call :meth:`batch_send` or
        :meth:`batch_forget`. If a batch has already been started, a
        :exc:`BatchStarted` exception is raised.

        .. note::

            This method can be used as a context manager
            (:ref:`the-with-statement`) which will cause a batch to be started,
            and implicitly terminated with :meth:`batch_send` or
            :meth:`batch_forget` depending on whether an exception is raised
            within the enclosed block.
        """
        if self._batch is not None:
            raise BatchStarted('batch already started')
        self._batch = []
        return self

    def batch_send(self):
        """
        Sends the batch transmission.

        This method is called after :meth:`batch_start` and :meth:`send` have
        been used to build up a list of batch commands. All the commands will
        be combined and sent to the server as a single transmission.

        If no batch is currently in progress, a :exc:`BatchNotStarted`
        exception will be raised.
        """
        if self._batch is None:
            raise BatchNotStarted('no batch in progress')
        self._send(''.join(self._batch))
        self._batch = None

    def batch_forget(self):
        """
        Terminates a batch transmission without sending anything.

        This method is called after :meth:`batch_start` and :meth:`send`
        have been used to build up a list of batch commands. All commands in
        the batch will be cleared without sending anything to the server.

        If no batch is currently in progress, a :exc:`BatchNotStarted`
        exception will be raised.
        """
        if self._batch is None:
            raise BatchNotStarted('no batch in progress')
        self._batch = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            self.batch_send()
        else:
            self.batch_forget()


class Game(object):
    """
    Represents a Minecraft game.

    This is the primary class that users interact with. Construct an instance
    of this class, optionally specifying the *host* and *port* of the server
    (which default to "localhost" and 4711 respectively). Afterward, the
    instance can be used to query and manipulate the minecraft world of the
    connected game.

    The :meth:`say` method can be used to send commands to the console, while
    the :attr:`player` attribute can be used to manipulate or query the status
    of the player character in the game. The :attr:`entities` attribute can be
    used to manipulate or query other objects within the game (this object can
    be iterated over to discover entities).
    """
    def __init__(self, host='localhost', port=4711):
        self.connection = Connection(host, port)

    def close(self):
        """
        Closes the connection to the game server.

        After this method is called, the game connection is closed and no
        further requests can be made. This method is implicitly called when
        the class is used as a context manager.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def say(self, message):
        """
        Displays *message* in the game's chat console.

        The *message* parameter must be a string (which may contain multiple
        lines). Each line of the message will be sent to the game's chat
        console and displayed immediately.
        """
        for line in message.splitlines():
            self.connection.send('chat.post(%s)\n' % line)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

