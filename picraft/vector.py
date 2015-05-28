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
The vector module defines the :class:`Vector` class, which is the usual method
of represent coordinates or vectors when dealing with the Minecraft world. It
also provides the :func:`vector_range` function for generating a sequence of
vectors.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.vector` directly.

The following items are defined in the module:


Vector
======

.. autoclass:: Vector(x, y, z)
    :members:


vector_range
============

.. autoclass:: vector_range(stop)
               vector_range(start, stop[, step])
    :members:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
try:
    range = xrange
except NameError:
    pass


import math
import operator as op
from functools import reduce, total_ordering
from collections import namedtuple
try:
    from itertools import zip_longest
except ImportError:
    # Py2 compat
    from itertools import izip_longest as zip_longest
try:
    from collections.abc import Sequence
except ImportError:
    # Py2 compat
    from collections import Sequence


class Vector(namedtuple('Vector', ('x', 'y', 'z'))):
    """
    Represents a 3-dimensional vector.

    This tuple derivative represents a 3-dimensional vector with x, y, z
    components. The class supports simple arithmetic operations with other
    vectors such as addition and subtraction, along with multiplication and
    division with scalars, raising to powers, bit-shifting, and so on.
    Attributes are provided for the :attr:`magnitude` of the vector, and a
    :attr:`unit` vector equivalent, along with methods for taking the
    :meth:`dot` and :meth:`cross` product with other vectors. For example::

        >>> v1 = Vector(1, 1, 1)
        >>> v2 = Vector(2, 2, 2)
        >>> v1 + v2
        Vector(x=3, y=3, z=3)
        >>> 2 * v2
        Vector(x=4, y=4, z=4)
        >>> Vector(z=1).magnitude
        1.0
        >>> Vector(x=1).cross(Vector(x=-1))
        Vector(x=0, y=0, z=0)

    Within the Minecraft world, the X,Z plane represents the ground, while the
    Y vector represents height.

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
    def from_string(cls, s, type=int):
        x, y, z = s.split(',', 2)
        return cls(type(x), type(y), type(z))

    def __str__(self):
        return '%s,%s,%s' % (self.x, self.y, self.z)

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

    def __pow__(self, other):
        try:
            return Vector(self.x ** other.x, self.y ** other.y, self.z ** other.z)
        except AttributeError:
            return Vector(self.x ** other, self.y ** other, self.z ** other)

    def __lshift__(self, other):
        try:
            return Vector(self.x << other.x, self.y << other.y, self.z << other.z)
        except AttributeError:
            return Vector(self.x << other, self.y << other, self.z << other)

    def __rshift__(self, other):
        try:
            return Vector(self.x >> other.x, self.y >> other.y, self.z >> other.z)
        except AttributeError:
            return Vector(self.x >> other, self.y >> other, self.z >> other)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __pos__(self):
        return self

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def __bool__(self):
        return bool(self.x or self.y or self.z)

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


product = lambda l: reduce(op.mul, l)

# TODO Yes, I'm being lazy with total_ordering ... probably ought to define all
# six comparison methods but I haven't got time right now ...

@total_ordering
class vector_range(Sequence):
    """
    Like :func:`range`, :class:`vector_range` is actually a type which
    efficiently represents a range of vectors. The arguments to the constructor
    must be :class:`Vector` instances (or objects which have integer ``x``,
    ``y``, and ``z`` attributes).

    If *step* is omitted, it defaults to ``Vector(1, 1, 1)``. If the *start*
    argument is omitted, it defaults to ``Vector(0, 0, 0)``. If any element
    of the *step* vector is zero, :exc:`ValueError` is raised.

    The contents of the range are largely determined by the *step* and *order*
    which specifies the order in which the axis of the range will be
    incremented.  For example, with the order ``'xyz'``, the X-axis will be
    incremented first, followed by the Y-axis, and finally the Z-axis. So, for
    a range with the default *start*, *step*, and *stop* set to ``Vector(3, 3,
    3)``, the contents of the range will be::

        >>> vector_range(Vector(3, 3, 3), order='xyz')
        [Vector(0, 0, 0), Vector(1, 0, 0), Vector(2, 0, 0),
         Vector(0, 1, 0), Vector(1, 1, 0), Vector(2, 1, 0),
         Vector(0, 2, 0), Vector(1, 2, 0), Vector(2, 2, 0),
         Vector(0, 0, 1), Vector(1, 0, 1), Vector(2, 0, 1),
         Vector(0, 1, 1), Vector(1, 1, 1), Vector(2, 1, 1),
         Vector(0, 2, 1), Vector(1, 2, 1), Vector(2, 2, 1),
         Vector(0, 0, 2), Vector(1, 0, 2), Vector(2, 0, 2),
         Vector(0, 1, 2), Vector(1, 1, 2), Vector(2, 1, 2),
         Vector(0, 2, 2), Vector(1, 2, 2), Vector(2, 2, 2)]

    Vector ranges implemented all common sequence operations except
    concatenation and repetition (due to the fact that range objects can only
    represent sequences that follow a strict pattern and repetition and
    concatenation usually cause the resulting sequence to violate that
    pattern).

    Vector ranges are extremely efficient compared to an equivalent
    :class:`list` or :class:`tuple` as they take a small (fixed) amount of
    memory, storing only the arguments passed in its construction and
    calculating individual items and sub-ranges as requested. All such
    calculations are done in fixed (O(1)) time.

    Vector range objects implement the :class:`collections.abc.Sequence` ABC,
    and provide features such as containment tests, element index lookup,
    slicing and support for negative indices.

    The default order (``'zxy'``) may seem an odd choice. This is primarily
    used as it's the order used by the Raspberry Juice server when returning
    results from the ``getBlocks`` call. In turn, Raspberry Juice probably uses
    this order as it results in returning a horizontal layer of vectors at a
    time (the Y-axis is used for height in the Minecraft world).

    .. warning::

        Bear in mind that the ordering of a vector range may have a bearing on
        tests for its ordering and equality. Two ranges with different orders
        are unlikely to test equal even though they may have the same *start*,
        *stop*, and *step* attributes (and thus contain the same vectors, but
        in a different order).
    """

    def __init__(
            self, start, stop=None, step=Vector(1, 1, 1), order='zxy',
            _slice=None):
        if stop is None:
            self._start = Vector()
            self._stop = start
        else:
            self._start = start
            self._stop = stop
        if order not in ('xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'):
            raise ValueError('invalid order: %s' % order)
        self._step = step
        self._order = order
        self._ranges = [
            range(
                getattr(self.start, axis),
                getattr(self.stop, axis),
                getattr(self.step, axis))
            for axis in order
            ]
        self._indexes = [
            order.index(axis)
            for axis in 'xyz'
            ]
        self._slice = None
        if _slice:
            assert len(_slice) <= len(self)
        self._slice = _slice

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    @property
    def order(self):
        return self._order

    def index(self, value):
        # XXX Do we need to support i and j arguments here? Python 3 defines
        # these in "common sequence operations" but ranges don't include them
        # TODO This is horrid (O(n)) - there must be a better way to do this
        # (O(1) maybe, but there's definitely an O(log(n)) way given that the
        # range output is effectively sorted). Unfortunatey I haven't got time
        # to explore it right now (ideally it'll involve reversing the divs and
        # mods in __getitem__, and I'd assume reversing the mods is vaguely
        # non-trivial in that it'll involve a set result)
        for result, v in enumerate(self):
            if v == value:
                return result
        raise ValueError('%r is not in range' % (value,))

    def count(self, value):
        # count is provided by the ABC but inefficiently; given no vectors in
        # the range can be duplicated we provide a more efficient version here
        if value in self:
            return 1
        else:
            return 0

    def __repr__(self):
        result = 'vector_range(%r, %r, %r, %r)' % (
                self.start, self.stop, self.step, self.order)
        if self._slice is not None:
            result += '[%d:%d:%d]' % (self._slice[0], self._slice[-1], self._slice.step)
        return result

    def __len__(self):
        if self._slice is None:
            return product(len(r) for r in self._ranges)
        else:
            return len(self._slice)

    def __lt__(self, other):
        for v1, v2 in zip_longest(self, other):
            if v1 < v2:
                return True
            elif v1 > v2:
                return False
        return False

    def __eq__(self, other):
        # Fast-path: if the other object is an identical vector_range we
        # can quickly test whether we're equal
        if isinstance(other, vector_range):
            if (
                    self.start == other.start and
                    self.stop == other.stop and
                    self.step == other.step and
                    self.order == other.order and
                    self._slice == other._slice):
                return True
        # TODO Any other fast-paths we can use here? E.g. what if item[0],
        # item[-1], step, and order are all equal; is that enough?
        # Fast path: if the other object has a len() we can quickly determine
        # whether we're not equal
        try:
            len(other)
        except TypeError:
            pass
        else:
            if len(self) != len(other):
                return False
        # Normal case: test every element in each sequence
        for v1, v2 in zip_longest(self, other):
            if v1 != v2:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]

    def __contains__(self, value):
        try:
            self.index(value)
        except ValueError:
            return False
        else:
            return True

    def __bool__(self):
        return len(self) > 0

    def __getitem__(self, index):
        if isinstance(index, slice):
            # XXX What about a slice of a slice?
            # Calculate the start and stop indexes
            start = index.start
            start = min(len(self), max(0, 0 if start is None else start + len(self) if start < 0 else start))
            stop = index.stop
            stop = min(len(self), max(0, len(self) if stop is None else stop + len(self) if stop < 0 else stop))
            step = 1 if index.step is None else index.step
            # If step is negative, flip the start and end
            if step < 0:
                start, stop = stop, start
                step = -step
            return vector_range(self.start, self.stop, self.step, self.order, range(start, stop, step))
        else:
            if index < 0:
                index += len(self)
            if not (0 <= index < len(self)):
                raise IndexError('list index out of range')
            if self._slice is not None:
                index = self._slice[index]
            v = (
                self._ranges[0][index % len(self._ranges[0])],
                self._ranges[1][(index // len(self._ranges[0])) % len(self._ranges[1])],
                self._ranges[2][index // (len(self._ranges[0]) * len(self._ranges[1]))],
                )
            return Vector(*(v[i] for i in self._indexes))

    # Py2 compat
    __nonzero__ = __bool__

