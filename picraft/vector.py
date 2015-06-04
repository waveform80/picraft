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


vector_range
============

.. autoclass:: vector_range
    :members:
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
from .compat import range


import sys
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
    components. Instances can be constructed in a number of ways. By explicitly
    specifying the x, y, and z components (optionally with keyword
    identifiers), or leaving the empty to default to 0::

        >>> Vector(1, 1, 1)
        Vector(x=1, y=1, z=1)
        >>> Vector(x=2, y=0, z=0)
        Vector(x=2, y=0, z=0)
        >>> Vector()
        Vector(x=0, y=0, z=0)
        >>> Vector(y=10)
        Vector(x=0, y=10, z=0)

    Note that vectors don't much care whether their components are integers,
    floating point values, or ``None``::

        >>> Vector(1.0, 1, 1)
        Vector(x=1.0, y=1, z=1)
        >>> Vector(2, None, None)
        Vector(x=2, y=None, z=None)

    The class supports simple arithmetic operations with other vectors such as
    addition and subtraction, along with multiplication and division with
    scalars, raising to powers, bit-shifting, and so on. Such operations are
    performed element-wise [1]_::

        >>> v1 = Vector(1, 1, 1)
        >>> v2 = Vector(2, 2, 2)
        >>> v1 + v2
        Vector(x=3, y=3, z=3)
        >>> 2 * v2
        Vector(x=4, y=4, z=4)

    Simple arithmetic operations with scalars return a new vector with that
    operation performed on all elements of the original. For example::

        >>> v = Vector()
        >>> v
        Vector(x=0, y=0, z=0)
        >>> v + 1
        Vector(x=1, y=1, z=1)
        >>> 2 * (v + 2)
        Vector(x=4, y=4, z=4)
        >>> Vector(y=2) ** 2
        Vector(x=0, y=4, z=0)

    Within the Minecraft world, the X,Z plane represents the ground, while the
    Y vector represents height.

    .. note::

        Note that, as a derivative of tuple, instances of this class are
        immutable. That is, you cannot directly manipulate the x, y, and z
        attributes; instead you must create a new vector (for example, by
        adding two vectors together). The advantage of this is that vector
        instances can be used in sets or as dictionary keys.

    .. [1] I realize math purists will hate this (and demand that abs() should
       be magnitude and * should invoke matrix multiplication), but the
       element wise operations are sufficiently useful to warrant the
       short-hand syntax.

    .. automethod:: dot

    .. automethod:: cross

    .. automethod:: distance_to

    .. attribute:: x

        The position or length of the vector along the X-axis. In the Minecraft
        world this can be considered to run left-to-right.

    .. attribute:: y

        The position or length of the vector along the Y-axis. In the Minecraft
        world this can be considered to run vertically up and down.

    .. attribute:: z

        The position or length of the vector along the Z-axis. In the Minecraft
        world this can be considered as depth (in or out of the screen).

    .. autoattribute:: magnitude

    .. autoattribute:: unit
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
        """
        Return the `dot product`_ of the vector with the *other* vector. The
        result is a scalar value. For example::

            >>> Vector(1, 2, 3).dot(Vector(2, 2, 2))
            12
            >>> Vector(1, 2, 3).dot(Vector(x=1))
            1

        .. _dot product: http://en.wikipedia.org/wiki/Dot_product
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """
        Return the `cross product`_ of the vector with the *other* vector. The
        result is another vector. For example::

            >>> Vector(1, 2, 3).cross(Vector(2, 2, 2))
            Vector(x=-2, y=4, z=-2)
            >>> Vector(1, 2, 3).cross(Vector(x=1))
            Vector(x=0, y=3, z=-2)

        .. _cross product: http://en.wikipedia.org/wiki/Cross_product
        """
        return Vector(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x)

    def distance_to(self, other):
        """
        Return the Euclidian distance between two three dimensional points
        (represented as vectors), calculated according to `Pythagoras'
        theorem`_. For example::

            >>> Vector(1, 2, 3).distance_to(Vector(2, 2, 2))
            1.4142135623730951
            >>> Vector().distance_to(Vector(x=1))
            1.0

        .. _Pythagoras' theorem: http://en.wikipedia.org/wiki/Pythagorean_theorem
        """
        return math.sqrt(
                (self.x - other.x) ** 2 +
                (self.y - other.y) ** 2 +
                (self.z - other.z) ** 2)

    @property
    def magnitude(self):
        """
        Returns the magnitude of the vector. This could also be considered the
        distance of the vector from the origin, i.e. ``v.magnitude`` is
        equivalent to ``Vector().distance_to(v)``. For example::

            >>> Vector(2, 4, 4).magnitude
            6.0
            >>> Vector().distance_to(Vector(2, 4, 4))
            6.0
        """
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @property
    def unit(self):
        """
        Return a `unit vector`_ (a vector with a magnitude of one) with the
        same direction as this vector::

            >>> Vector(1, 0, 0).unit
            Vector(x=1.0, y=0.0, z=0.0)
            >>> Vector(0, 2, 0).unit
            Vector(x=0.0, y=1.0, z=0.0)

        .. note::

            If the vector's magnitude is zero, this property returns the
            original vector.

        .. _unit vector: http://en.wikipedia.org/wiki/Unit_vector
        """
        if self.magnitude > 0:
            return self / self.magnitude
        else:
            return self


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
    which specifies the order in which the axes of the range will be
    incremented.  For example, with the order ``'xyz'``, the X-axis will be
    incremented first, followed by the Y-axis, and finally the Z-axis. So, for
    a range with the default *start*, *step*, and *stop* set to ``Vector(3, 3,
    3)``, the contents of the range will be::

        >>> list(vector_range(Vector(3, 3, 3), order='xyz'))
        [Vector(0, 0, 0), Vector(1, 0, 0), Vector(2, 0, 0),
         Vector(0, 1, 0), Vector(1, 1, 0), Vector(2, 1, 0),
         Vector(0, 2, 0), Vector(1, 2, 0), Vector(2, 2, 0),
         Vector(0, 0, 1), Vector(1, 0, 1), Vector(2, 0, 1),
         Vector(0, 1, 1), Vector(1, 1, 1), Vector(2, 1, 1),
         Vector(0, 2, 1), Vector(1, 2, 1), Vector(2, 2, 1),
         Vector(0, 0, 2), Vector(1, 0, 2), Vector(2, 0, 2),
         Vector(0, 1, 2), Vector(1, 1, 2), Vector(2, 1, 2),
         Vector(0, 2, 2), Vector(1, 2, 2), Vector(2, 2, 2)]

    Vector ranges implement all common sequence operations except concatenation
    and repetition (due to the fact that range objects can only represent
    sequences that follow a strict pattern and repetition and concatenation
    usually cause the resulting sequence to violate that pattern).

    Vector ranges are extremely efficient compared to an equivalent
    :class:`list` or :class:`tuple` as they take a small (fixed) amount of
    memory, storing only the arguments passed in its construction and
    calculating individual items and sub-ranges as requested.

    Vector range objects implement the :class:`collections.abc.Sequence` ABC,
    and provide features such as containment tests, element index lookup,
    slicing and support for negative indices.

    The default order (``'zxy'``) may seem an odd choice. This is primarily
    used as it's the order used by the Raspberry Juice server when returning
    results from the ``getBlocks`` call. In turn, Raspberry Juice probably uses
    this order as it results in returning a horizontal layer of vectors at a
    time (given the Y-axis is used for height in the Minecraft world).

    .. warning::

        Bear in mind that the ordering of a vector range may have a bearing on
        tests for its ordering and equality. Two ranges with different orders
        are unlikely to test equal even though they may have the same *start*,
        *stop*, and *step* attributes (and thus contain the same vectors, but
        in a different order).

    Vector ranges can be accessed by integer index, by :class`Vector` index,
    or by a slice of vectors. For example::

        >>> v = vector_range(Vector() + 1, Vector() + 3)
        >>> list(v)
        [Vector(x=1, y=1, z=1),
         Vector(x=1, y=1, z=2),
         Vector(x=2, y=1, z=1),
         Vector(x=2, y=1, z=2),
         Vector(x=1, y=2, z=1),
         Vector(x=1, y=2, z=2),
         Vector(x=2, y=2, z=1),
         Vector(x=2, y=2, z=2)]
        >>> v[0]
        Vector(x=1, y=1, z=1)
        >>> v[Vector(0, 0, 0)]
        Vector(x=1, y=1, z=1)
        >>> v[Vector(1, 0, 0)]
        Vector(x=2, y=1, z=1)
        >>> v[-1]
        Vector(x=2, y=2, z=2)
        >>> v[Vector() - 1]
        Vector(x=2, y=2, z=2)
        >>> v[Vector(x=1):]
        vector_range(Vector(x=2, y=1, z=1), Vector(x=3, y=3, z=3),
                Vector(x=1, y=1, z=1), order='zxy')
        >>> list(v[Vector(x=1):])
        [Vector(x=2, y=1, z=1),
         Vector(x=2, y=1, z=2),
         Vector(x=2, y=2, z=1),
         Vector(x=2, y=2, z=2)]

    However, integer slices are not currently permitted.
    """

    def __init__(
            self, start, stop=None, step=Vector(1, 1, 1), order='zxy'):
        if stop is None:
            start, stop = Vector(), start
        if (start != start // 1) or (stop != stop // 1) or (step != step // 1):
            raise TypeError('integer vectors are required')
        if order not in ('xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'):
            raise ValueError('invalid order: %s' % order)
        if not (step.x and step.y and step.z):
            raise ValueError('no element of step may be zero')
        self._start = start
        self._stop = stop
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
        self._xrange, self._yrange, self._zrange = (
            self._ranges[i] for i in self._indexes
            )

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

    def __repr__(self):
        if self.start == Vector() and self.step == Vector() + 1:
            return 'vector_range(%r, order=%r)' % (self.stop, self.order)
        elif self.step == Vector() + 1:
            return 'vector_range(%r, %r, order=%r)' % (
                    self.start, self.stop, self.order)
        else:
            return 'vector_range(%r, %r, %r, order=%r)' % (
                    self.start, self.stop, self.step, self.order)

    def __len__(self):
        return product(len(r) for r in self._ranges)

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
            return (
                    self._xrange == other._xrange and
                    self._yrange == other._yrange and
                    self._zrange == other._zrange and
                    self.order == other.order
                    )
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

    # Py2 compat
    __nonzero__ = __bool__

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._get_slice(index)
        elif isinstance(index, Vector):
            try:
                return Vector(*(
                    self._ranges[i][j]
                    for i, j in zip(self._indexes, index)
                    ))
            except IndexError:
                raise IndexError('list index out of range')
        else:
            if index < 0:
                index += len(self)
            if not (0 <= index < len(self)):
                raise IndexError('list index out of range')
            v = (
                self._ranges[0][index % len(self._ranges[0])],
                self._ranges[1][(index // len(self._ranges[0])) % len(self._ranges[1])],
                self._ranges[2][index // (len(self._ranges[0]) * len(self._ranges[1]))],
                )
            return Vector(*(v[i] for i in self._indexes))

    def _get_slice(self, s):
        try:
            step = Vector() + 1 if s.step is None else s.step
            start = Vector(None, None, None) if s.start is None else s.start
            stop = Vector(None, None, None) if s.stop is None else s.stop
            if not (step.x and step.y and step.z):
                raise ValueError(
                    "every element of the slice's step must be non-zero")
            x_range = self._xrange[slice(start.x, stop.x, step.x)]
            y_range = self._yrange[slice(start.y, stop.y, step.y)]
            z_range = self._zrange[slice(start.z, stop.z, step.z)]
        except AttributeError:
            raise ValueError(
                "vector_range slices must be composed of Vectors")
        return vector_range(
            Vector(x_range.start, y_range.start, z_range.start),
            Vector(x_range.stop, y_range.stop, z_range.stop),
            Vector(x_range.step, y_range.step, z_range.step),
            self.order)

    def index(self, value):
        """
        Return the zero-based index of *value* within the range, or raise
        :exc:`ValueError` if *value* does not exist in the range.
        """
        ranges = self._ranges
        i, j, k = (getattr(value, axis) for axis in self.order)
        l = product(len(r) for r in self._ranges)
        try:
            i_indexes = set(rmod(len(ranges[0]), ranges[0].index(i), range(l)))
            j_indexes = set(
                    b
                    for a in rmod(len(ranges[1]), ranges[1].index(j),
                        range(l // len(ranges[0])))
                    for b in rdiv(len(ranges[0]), a)
                    )
            k_indexes = set(rdiv(len(ranges[0]) * len(ranges[1]), ranges[2].index(k)))
            result = i_indexes & j_indexes & k_indexes
            assert len(result) == 1
            result = next(iter(result))
        except ValueError:
            raise ValueError('%r is not in range' % (value,))
        else:
            return result

    def count(self, value):
        """
        Return the count of instances of *value* within the range (note this
        can only be 0 or 1 in the case of a range, and thus is equivalent to
        testing membership with ``in``).
        """
        # count is provided by the ABC but inefficiently; given no vectors in
        # the range can be duplicated we provide a more efficient version here
        if value in self:
            return 1
        else:
            return 0


def product(l):
    """
    Return the product of all values in the list *l*"
    """
    return reduce(op.mul, l)


def rmod(denom, result, num_range):
    """
    Calculates the inverse of a mod operation.

    The *denom* parameter specifies the denominator of the original mod (%)
    operation. In this implementation, *denom* must be greater than 0. The
    *result* parameter specifies the result of the mod operation. For obvious
    reasons this value must be in the range ``[0, denom)`` (greater than or
    equal to zero and less than the denominator).

    Finally, *num_range* specifies the range that the numerator of the original
    mode operation can lie in. This must be an iterable sorted in ascending
    order with unique values (e.g. most typically a :func:`range`).

    The function returns the set of potential numerators (guaranteed to be a
    subset of *num_range*).
    """
    if denom <= 0:
        raise ValueError('invalid denominator')
    if not (0 <= result < denom):
        return set()
    if len(num_range) == 0:
        return set()
    assert num_range[-1] >= num_range[0]
    start = num_range[0] + (result - num_range[0] % denom) % denom
    stop = num_range.stop
    return range(start, stop, denom)


def rdiv(denom, result):
    """
    Calculates the inverse of a div operation.

    The *denom* parameter specifies the denominator of the original div (//)
    operation. In this implementation, *denom* must be greater than 0. The
    *result* parameter specifies the result of the div operation.

    The function returns the set of potential numerators.
    """
    if denom <= 0:
        raise ValueError('invalid denominator')
    return range(result * denom, result * denom + denom)


