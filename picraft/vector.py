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
The vector module defines the :class:`Vector` class, which is the usual method
of representing coordinates or vectors when dealing with the Minecraft world.
It also provides functions like :func:`vector_range` for generating sequences
of vectors.

.. note::

    All items in this module are available from the :mod:`picraft` namespace
    without having to import :mod:`picraft.vector` directly.

The following items are defined in the module:


Vector
======

.. autoclass:: Vector(x=0, y=0, z=0)


Short-hand variants
===================

The :class:`Vector` class is used sufficiently often to justify the inclusion
of some shortcuts. The class itself is also available as ``V``, and vectors
representing the three axes are each available as ``X``, ``Y``, and ``Z``.
Finally, a vector representing the origin is available as ``O``::

    >>> from picraft import V, O, X, Y, Z
    >>> O
    Vector(x=0, y=0, z=0)
    >>> 2 * X
    Vector(x=2, y=0, z=0)
    >>> X + Y
    Vector(x=1, y=1, z=0)
    >>> (X + Y).angle_between(X)
    45.00000000000001
    >>> V(3, 4, 5).projection(X)
    3.0
    >>> X.rotate(90, about=Y)
    Vector(x=0.0, y=0.0, z=1.0)


vector_range
============

.. autoclass:: vector_range
    :members:


line
====

.. autofunction:: line


lines
=====

.. autofunction:: lines


circle
======

.. autofunction:: circle


sphere
======

.. autofunction:: sphere


filled
======

.. autofunction:: filled
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
from .compat import range


import math
from functools import total_ordering
from collections import namedtuple, Sequence
try:
    from itertools import zip_longest, islice, tee
except ImportError:
    # Py2 compat
    from itertools import izip_longest as zip_longest, islice, tee


class Vector(namedtuple('Vector', ('x', 'y', 'z'))):
    """
    Represents a 3-dimensional vector.

    This :func:`~collections.namedtuple` derivative represents a 3-dimensional
    vector with :attr:`x`, :attr:`y`, :attr:`z` components. Instances can be
    constructed in a number of ways: by explicitly specifying the x, y, and z
    components (optionally with keyword identifiers), or leaving them empty to
    default to 0::

        >>> Vector(1, 1, 1)
        Vector(x=1, y=1, z=1)
        >>> Vector(x=2, y=0, z=0)
        Vector(x=2, y=0, z=0)
        >>> Vector()
        Vector(x=0, y=0, z=0)
        >>> Vector(y=10)
        Vector(x=0, y=10, z=0)

    Shortcuts are available for vectors representing the X, Y, and Z axes::

        >>> X
        Vector(x=1, y=0, z=0)
        >>> Y
        Vector(x=0, y=1, z=0)

    Note that vectors don't much care whether their components are integers,
    floating point values, or ``None``::

        >>> Vector(1.0, 1, 1)
        Vector(x=1.0, y=1, z=1)
        >>> Vector(2, None, None)
        Vector(x=2, y=None, z=None)

    The class supports simple arithmetic operations with other vectors such as
    addition and subtraction, along with multiplication and division, raising
    to powers, bit-shifting, and so on. Such operations are performed
    element-wise [1]_::

        >>> v1 = Vector(1, 1, 1)
        >>> v2 = Vector(2, 2, 2)
        >>> v1 + v2
        Vector(x=3, y=3, z=3)
        >>> v1 * v2
        Vector(x=2, y=2, z=2)

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

        Note that, as a derivative of :func:`~collections.namedtuple`,
        instances of this class are immutable. That is, you cannot directly
        manipulate the :attr:`x`, :attr:`y`, and :attr:`z` attributes; instead
        you must create a new vector (for example, by adding two vectors
        together). The advantage of this is that vector instances can be
        members of a :class:`set` or keys in a :class:`dict`.

    .. [1] I realize math purists will hate this (and demand that abs() should
       be magnitude and * should invoke matrix multiplication), but the
       element wise operations are sufficiently useful to warrant the
       short-hand syntax.

    .. automethod:: replace

    .. automethod:: ceil

    .. automethod:: floor

    .. automethod:: dot

    .. automethod:: cross

    .. automethod:: distance_to

    .. automethod:: angle_between

    .. automethod:: project

    .. automethod:: rotate

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

    __slots__ = () # workaround python issue #24931

    def __new__(cls, x=0, y=0, z=0):
        return super(Vector, cls).__new__(cls, x, y, z)

    @classmethod
    def from_string(cls, s, type=int):
        x, y, z = s.split(',')
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

    def __pow__(self, other, modulo=None):
        if modulo is not None:
            try:
                # XXX What about other vector, modulo scalar, and other scalar, modulo vector?
                return Vector(
                        pow(self.x, other.x, modulo.x),
                        pow(self.y, other.y, modulo.y),
                        pow(self.z, other.z, modulo.z))
            except AttributeError:
                return Vector(
                        pow(self.x, other, modulo),
                        pow(self.y, other, modulo),
                        pow(self.z, other, modulo))
        try:
            return Vector(
                    pow(self.x, other.x),
                    pow(self.y, other.y),
                    pow(self.z, other.z))
        except AttributeError:
            return Vector(
                    pow(self.x, other),
                    pow(self.y, other),
                    pow(self.z, other))

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

    def __and__(self, other):
        try:
            return Vector(self.x & other.x, self.y & other.y, self.z & other.z)
        except AttributeError:
            return Vector(self.x & other, self.y & other, self.z & other)

    def __xor__(self, other):
        try:
            return Vector(self.x ^ other.x, self.y ^ other.y, self.z ^ other.z)
        except AttributeError:
            return Vector(self.x ^ other, self.y ^ other, self.z ^ other)

    def __or__(self, other):
        try:
            return Vector(self.x | other.x, self.y | other.y, self.z | other.z)
        except AttributeError:
            return Vector(self.x | other, self.y | other, self.z | other)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __pos__(self):
        return self

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def __bool__(self):
        return bool(self.x or self.y or self.z)

    def __trunc__(self):
        return Vector(math.trunc(self.x), math.trunc(self.y), math.trunc(self.z))

    # Py2 compat
    __nonzero__ = __bool__
    __div__ = __truediv__

    def replace(self, x=None, y=None, z=None):
        """
        Return the vector with the x, y, or z axes replaced with the specified
        values. For example::

            >>> Vector(1, 2, 3).replace(z=4)
            Vector(x=1, y=2, z=4)
        """
        # XXX What if I want to use None?
        return Vector(
            self.x if x is None else x,
            self.y if y is None else y,
            self.z if z is None else z)

    def floor(self):
        """
        Return the vector with the floor of each component. This is only useful
        for vectors containing floating point components::

            >>> Vector(0.5, -0.5, 1.9)
            Vector(0.0, -1.0, 1.0)
        """
        return Vector(
            int(math.floor(self.x)),
            int(math.floor(self.y)),
            int(math.floor(self.z)))

    def ceil(self):
        """
        Return the vector with the ceiling of each component. This is only
        useful for vectors containing floating point components::

            >>> Vector(0.5, -0.5, 1.2)
            Vector(1.0, 0.0, 2.0)
        """
        return Vector(
            int(math.ceil(self.x)),
            int(math.ceil(self.y)),
            int(math.ceil(self.z)))

    def round(self, ndigits=0):
        """
        Return the vector with the rounded value of each component. This is
        only useful for vectors containing floating point components::

            >>> Vector(0.5, -0.5, 1.2)
            Vector(1.0, -1.0, 1.0)

        The *ndigits* argument operates as it does in the built-in
        :func:`round` function, specifying the number of decimal (or integer)
        places to round to.
        """
        if ndigits <= 0:
            return Vector(
                int(round(self.x, ndigits)),
                int(round(self.y, ndigits)),
                int(round(self.z, ndigits)))
        else:
            return Vector(
                round(self.x, ndigits),
                round(self.y, ndigits),
                round(self.z, ndigits))

    def dot(self, other):
        """
        Return the `dot product`_ of the vector with the *other* vector. The
        result is a scalar value. For example::

            >>> Vector(1, 2, 3).dot(Vector(2, 2, 2))
            12
            >>> Vector(1, 2, 3).dot(X)
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
            >>> Vector(1, 2, 3).cross(X)
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
            >>> O.distance_to(X)
            1.0

        .. _Pythagoras' theorem: http://en.wikipedia.org/wiki/Pythagorean_theorem
        """
        return (other - self).magnitude

    def angle_between(self, other):
        """
        Returns the angle between this vector and the *other* vector on a plane
        that contains both vectors. The result is measured in degrees between 0
        and 180. For example::

            >>> X.angle_between(Y)
            90.0
            >>> (X + Y).angle_between(X)
            45.00000000000001
        """
        return math.degrees(math.acos(self.unit.dot(other.unit)))

    def project(self, other):
        """
        Return the `scalar projection`_ of this vector onto the *other* vector.
        This is a scalar indicating the length of this vector in the direction
        of the *other* vector. For example::

            >>> Vector(1, 2, 3).project(2 * Y)
            2.0
            >>> Vector(3, 4, 5).project(Vector(3, 4, 0))
            5.0

        .. _scalar projection: https://en.wikipedia.org/wiki/Scalar_projection
        """
        return self.dot(other.unit)

    def rotate(self, angle, about, origin=None):
        """
        Return this vector after `rotation`_ of *angle* degrees about the line
        passing through *origin* in the direction *about*. Origin defaults to
        the vector 0, 0, 0. Hence, if this parameter is omitted this method
        calculates rotation about the axis (through the origin) defined by
        *about*.  For example::

            >>> Y.rotate(90, about=X)
            Vector(x=0, y=6.123233995736766e-17, z=1.0)
            >>> Vector(3, 4, 5).rotate(30, about=X, origin=10 * Y)
            Vector(x=3.0, y=2.3038475772933684, z=1.330127018922194)

        Information about rotation around arbitrary lines was obtained from
        `Glenn Murray's informative site`_.

        .. _rotation: https://en.wikipedia.org/wiki/Rotation_group_SO%283%29
        .. _Glenn Murray's informative site: http://inside.mines.edu/fs_home/gmurray/ArbitraryAxisRotation/
        """
        r = math.radians(angle)
        sin = math.sin(r)
        cos = math.cos(r)
        x, y, z = self
        if origin is None:
            # Fast-paths: rotation about a specific unit axis
            if about == X:
                return Vector(x, y * cos - z * sin, y * sin + z * cos)
            elif about == Y:
                return Vector(z * sin + x * cos, y, z * cos - x * sin)
            elif about == Z:
                return Vector(x * cos - y * sin, x * sin + y * cos, z)
            elif about == negX:
                return Vector(x, y * cos + z * sin, z * cos - y * sin)
            elif about == negY:
                return Vector(x * cos - z * sin, y, z * cos + x * sin)
            elif about == negZ:
                return Vector(x * cos + y * sin, y * cos - x * sin, z)
            # Rotation about an arbitrary axis
            u, v, w = about.unit
            return Vector(
                u * (u * x + v * y + w * z) * (1 - cos) + x * cos + (-w * y + v * z) * sin,
                v * (u * x + v * y + w * z) * (1 - cos) + y * cos + ( w * x - u * z) * sin,
                w * (u * x + v * y + w * z) * (1 - cos) + z * cos + (-v * x + u * y) * sin)
        # Rotation about an arbitrary line
        a, b, c = origin
        u, v, w = about.unit
        return Vector(
            (a * (v ** 2 + w ** 2) - u * (b * v + c * w - u * x - v * y - w * z)) * (1 - cos) + x * cos + (-c * v + b * w - w * y + v * z) * sin,
            (b * (u ** 2 + w ** 2) - v * (a * u + c * w - u * x - v * y - w * z)) * (1 - cos) + y * cos + ( c * u - a * w + w * x - u * z) * sin,
            (c * (u ** 2 + v ** 2) - w * (a * u + b * v - u * x - v * y - w * z)) * (1 - cos) + z * cos + (-b * u + a * v - v * x + u * y) * sin)

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

            >>> X.unit
            Vector(x=1.0, y=0.0, z=0.0)
            >>> (2 * Y).unit
            Vector(x=0.0, y=1.0, z=0.0)

        .. note::

            If the vector's magnitude is zero, this property returns the
            original vector.

        .. _unit vector: http://en.wikipedia.org/wiki/Unit_vector
        """
        try:
            return self / self.magnitude
        except ZeroDivisionError:
            return self


# Short-hand variants
V = Vector
O = V()
X = V(x=1)
Y = V(y=1)
Z = V(z=1)
# These aren't exposed as short-hands; they're only pre-calculated here to
# speed up the fast-paths in the rotate() method
negX = V(x=-1)
negY = V(y=-1)
negZ = V(z=-1)


# XXX Yes, I'm being lazy with total_ordering ... probably ought to define all
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
    :func:`list` or :func:`tuple` as they take a small (fixed) amount of
    memory, storing only the arguments passed in its construction and
    calculating individual items and sub-ranges as requested.

    Vector range objects implement the :class:`collections.Sequence` ABC,
    and provide features such as containment tests, element index lookup,
    slicing and support for negative indices.

    The default order (``'zxy'``) may seem an odd choice. This is primarily
    used as it's the order used by the Raspberry Juice server when returning
    results from the :ref:`world.getBlocks` call. In turn, Raspberry Juice
    probably uses this order as it results in returning a horizontal layer of
    vectors at a time (given the Y-axis is used for height in the Minecraft
    world).

    .. warning::

        Bear in mind that the ordering of a vector range may have affect tests
        for its ordering and equality. Two ranges with different orders are
        unlikely to test equal even though they may have the same *start*,
        *stop*, and *step* attributes (and thus contain the same vectors, but
        in a different order).

    Vector ranges can be accessed by integer index, by :class:`Vector` index,
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
            self, start, stop=None, step=None, order='zxy'):
        if stop is None:
            start, stop = Vector(), start
        if step is None:
            step = Vector(1, 1, 1)
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
                getattr(start, axis),
                getattr(stop, axis),
                getattr(step, axis))
            for axis in order
            ]
        self._indexes = [
            order.index(axis)
            for axis in 'xyz'
            ]
        self._xrange, self._yrange, self._zrange = (
            self._ranges[i] for i in self._indexes
            )
        self._len = len(self._xrange) * len(self._yrange) * len(self._zrange)

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
        return self._len

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
        try:
            i_indexes = set(rmod(len(ranges[0]), ranges[0].index(i), range(len(self))))
            j_indexes = set(
                    b
                    for a in rmod(len(ranges[1]), ranges[1].index(j),
                        range(len(self) // len(ranges[0])))
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


def sign(v):
    """
    Returns the sign of v as -1, 0, or 1; works for scalar values or
    :class:`Vector` instances.
    """
    try:
        return Vector(sign(v.x), sign(v.y), sign(v.z))
    except AttributeError:
        return 1 if v > 0 else -1 if v < 0 else 0


def line(start, end):
    """
    Generates the coordinates of a line joining the *start* and *end*
    :class:`Vector` instances inclusive. This is a generator function; points
    are yielded from *start*, proceeding to *end*. If you don't require all
    points you may terminate the generator at any point.

    For example::

        >>> list(line(O, V(10, 5, 0)))
        [Vector(x=0, y=0, z=0),
         Vector(x=1, y=1, z=0),
         Vector(x=2, y=1, z=0),
         Vector(x=3, y=2, z=0),
         Vector(x=4, y=2, z=0),
         Vector(x=5, y=3, z=0),
         Vector(x=6, y=3, z=0),
         Vector(x=7, y=4, z=0),
         Vector(x=8, y=4, z=0),
         Vector(x=9, y=5, z=0),
         Vector(x=10, y=5, z=0)]

    To draw the resulting line you can simply assign a block to the collection
    of vectors generated (or assign a sequence of blocks of equal length if you
    want the line to have varying block types)::

        >>> world.blocks[line(O, V(10, 5, 0))] = Block('stone')

    This is a three-dimensional implementation of `Bresenham's line
    algorithm`_, derived largely from `Bob Pendelton's implementation`_ (public
    domain).

    .. _Bresenham's line algorithm: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    .. _Bob Pendelton's implementation: ftp://ftp.isc.org/pub/usenet/comp.sources.unix/volume26/line3d
    """
    delta = end - start
    # Calculate the amount to increment each axis by; only the dominant axis
    # will advance by this amount on *every* iteration. Other axes will only
    # increment when the error demands it
    pos_inc = sign(delta)
    # Set up a vector containing the error incrementor. This will be added to
    # values tracking the axis error on each iteration
    error_inc = abs(delta) << 1
    # Calculate the subordinate and dominant axes. The dominant axis is simply
    # the one in which we must move furthest
    sub_axis1, sub_axis2, dominant_axis = sorted(
            'xyz', key=lambda axis: getattr(error_inc, axis))
    # Set up the error decrementor. This will be subtracted from the error
    # values when they turn positive (indicating that the corresponding axis
    # should advance)
    error_dec = getattr(error_inc, dominant_axis)
    # Set up a vector to track the error (this is only really required for the
    # subordinate axes)
    error = error_inc - (error_dec >> 1)
    # Convert vectors to dicts for the remainder of the algorithm
    error = error._asdict()
    error_inc = error_inc._asdict()
    pos_inc = pos_inc._asdict()
    pos = start._asdict()
    end = getattr(end, dominant_axis)
    while True:
        yield Vector(**pos)
        if pos[dominant_axis] == end:
            break
        pos[dominant_axis] += pos_inc[dominant_axis]
        if error[sub_axis1] >= 0:
            pos[sub_axis1] += pos_inc[sub_axis1]
            error[sub_axis1] -= error_dec
        error[sub_axis1] += error_inc[sub_axis1]
        if error[sub_axis2] >= 0:
            pos[sub_axis2] += pos_inc[sub_axis2]
            error[sub_axis2] -= error_dec
        error[sub_axis2] += error_inc[sub_axis2]


def lines(points, closed=True):
    """
    Generator function which extends the :func:`line` function; this yields all
    vectors necessary to render the lines connecting the specified *points*
    (which is an iterable of :class:`Vector` instances).

    If the optional *closed* parameter is ``True`` (the default) the last point
    in the *points* sequence will be connected to the first point. Otherwise,
    the lines will be left disconnected (assuming the last point is not
    coincident with the first). For example::

        >>> points = [O, 4*X, 4*Z]
        >>> list(lines(points))
        [Vector(x=0, y=0, z=0),
         Vector(x=1, y=0, z=0),
         Vector(x=2, y=0, z=0),
         Vector(x=3, y=0, z=0),
         Vector(x=4, y=0, z=0),
         Vector(x=3, y=0, z=1),
         Vector(x=2, y=0, z=2),
         Vector(x=1, y=0, z=3),
         Vector(x=0, y=0, z=4),
         Vector(x=0, y=0, z=3),
         Vector(x=0, y=0, z=2),
         Vector(x=0, y=0, z=1),
         Vector(x=0, y=0, z=0)]

    To draw the resulting polygon you can simply assign a block to the
    collection of vectors generated (or assign a sequence of blocks of equal
    length if you want the polygon to have varying block types)::

        >>> world.blocks[lines(points)] = Block('stone')

    To generate the coordinates of a filled polygon, see the :func:`filled`
    function.
    """
    first = None
    start = None
    point = None
    for point in points:
        if start is None:
            first = point
            yield first
        else:
            for v in islice(line(start, point), 1, None):
                yield v
        start = point
    if point is None:
        raise ValueError('no points specified')
    if closed and first != point:
        for v in islice(line(point, first), 1, None):
            yield v


def circle(center, radius, plane=Y):
    """
    Generator function which yields the coordinates of a three-dimensional
    circle centered at the :class:`Vector` *center*. The *radius* parameter is
    a vector specifying the distance of the circumference from the center. The
    optional *plane* parameter (which defaults to the Y unit vector) specifies
    another vector which, in combination with the *radius* vector, gives the
    plane that the circle exists within.

    For example, to generate the coordinates of a circle centered at (0, 10,
    0), with a radius of 5 units, existing in the X-Y plane::

        >>> list(circle(O, 5*X))
        [Vector(x=-5, y=0, z=0), Vector(x=-5, y=1, z=0), Vector(x=-4, y=2, z=0),
         Vector(x=-4, y=3, z=0), Vector(x=-5, y=-1, z=0), Vector(x=-4, y=-2, z=0),
         Vector(x=-4, y=-3, z=0), Vector(x=-3, y=4, z=0), Vector(x=-3, y=-4, z=0),
         Vector(x=-2, y=4, z=0), Vector(x=-2, y=-4, z=0), Vector(x=-1, y=4, z=0),
         Vector(x=-1, y=-4, z=0), Vector(x=0, y=5, z=0), Vector(x=0, y=-5, z=0),
         Vector(x=1, y=4, z=0), Vector(x=1, y=-4, z=0), Vector(x=2, y=4, z=0),
         Vector(x=2, y=-4, z=0), Vector(x=3, y=4, z=0), Vector(x=3, y=-4, z=0),
         Vector(x=4, y=3, z=0), Vector(x=4, y=-3, z=0), Vector(x=4, y=2, z=0),
         Vector(x=5, y=1, z=0), Vector(x=5, y=0, z=0), Vector(x=4, y=-2, z=0),
         Vector(x=5, y=-1, z=0)]

    To generate another set of coordinates with the same center and radius, but
    existing in the X-Z (ground) plane::

        >>> list(circle(O, 5*X, plane=Z))
        [Vector(x=-5, y=0, z=0), Vector(x=-5, y=0, z=1), Vector(x=-4, y=0, z=2),
         Vector(x=-4, y=0, z=3), Vector(x=-5, y=0, z=-1), Vector(x=-4, y=0, z=-2),
         Vector(x=-4, y=0, z=-3), Vector(x=-3, y=0, z=4), Vector(x=-3, y=0, z=-4),
         Vector(x=-2, y=0, z=4), Vector(x=-2, y=0, z=-4), Vector(x=-1, y=0, z=4),
         Vector(x=-1, y=0, z=-4), Vector(x=0, y=0, z=5), Vector(x=0, y=0, z=-5),
         Vector(x=1, y=0, z=4), Vector(x=1, y=0, z=-4), Vector(x=2, y=0, z=4),
         Vector(x=2, y=0, z=-4), Vector(x=3, y=0, z=4), Vector(x=3, y=0, z=-4),
         Vector(x=4, y=0, z=3), Vector(x=4, y=0, z=-3), Vector(x=4, y=0, z=2),
         Vector(x=5, y=0, z=1), Vector(x=5, y=0, z=0), Vector(x=4, y=0, z=-2),
         Vector(x=5, y=0, z=-1)]

    To draw the resulting circle you can simply assign a block to the
    collection of vectors generated (or assign a sequence of blocks of equal
    length if you want the circle to have varying block types)::

        >>> world.blocks[circle(O, 5*X)] = Block('stone')

    The algorithm used by this function is based on a straight-forward
    differences of roots method, extended to three dimensions. This produces
    `worse looking`_ circles than the `midpoint circle algorithm`_ (also known
    as a the Bresenham circle algorithm), but isn't restricted to working in a
    simple cartesian plane.

    .. note::

        If you know of a three dimensional generalization of the midpoint
        circle algorithm (which handles entirely arbitrary planes, not merely
        simple X-Y, X-Z, etc. planes), please contact the `author`_!

    To create a filled circle, see the :func:`filled` function.

    .. _worse looking: https://sites.google.com/site/ruslancray/lab/projects/bresenhamscircleellipsedrawingalgorithm/bresenham-s-circle-ellipse-drawing-algorithm
    .. _midpoint circle algorithm: https://en.wikipedia.org/wiki/Midpoint_circle_algorithm
    .. _author: mailto:dave@waveform.org.uk
    """
    try:
        if radius.angle_between(plane) != 90:
            plane = radius.cross(-(radius.cross(plane)))
    except AttributeError:
        raise ValueError('radius must be a Vector instance')
    perp = plane.unit
    r = radius.magnitude**2
    last_points = None
    result = set()
    result_len = 0
    for radial_point in line(-radius, radius):
        circum_v = (perp * math.sqrt(r - radial_point.magnitude**2)).floor()
        top_point = (radial_point + circum_v)
        bottom_point = (radial_point - circum_v)
        if last_points is not None:
            top_last, bottom_last = last_points
            for p in line(top_last, top_point):
                p += center
                result.add(p)
                if len(result) > result_len:
                    result_len += 1
                    yield p
            for p in line(bottom_last, bottom_point):
                p += center
                result.add(p)
                if len(result) > result_len:
                    result_len += 1
                    yield p
        last_points = top_point, bottom_point


def sphere(center, radius):
    """
    Generator function which yields the coordinates of a hollow sphere. The
    *center* :class:`Vector` specifies the center of the sphere, and *radius*
    is a scalar number of blocks giving the distance from the center to the
    edge of the sphere.

    For example to create the coordinates of a sphere centered at the origin
    with a radius of 5 units::

        >>> list(sphere(O, 5))

    To draw the resulting sphere you can simply assign a block to the
    collection of vectors generated (or assign a sequence of blocks of equal
    length if you want the sphere to have varying block types)::

        >>> world.blocks[sphere(O, 5)] = Block('stone')

    The algorithm generates concentric circles covering the sphere's surface,
    advancing along the X, Y, and Z axes with duplicate elimination to prevent
    repeated coordinates being yielded. Three axes are required to eliminate
    gaps in the surface.
    """
    r = radius**2
    last_points = None
    result = set()
    result_len = 0
    for radial_point in range(-radius, radius + 1):
        circum_dist = int(round(math.sqrt(r - radial_point**2)))
        for p in circle(X * radial_point, Z * circum_dist):
            p += center
            result.add(p)
            if len(result) > result_len:
                result_len += 1
                yield p
        for p in circle(Y * radial_point, Z * circum_dist, plane=X):
            p += center
            result.add(p)
            if len(result) > result_len:
                result_len += 1
                yield p
        for p in circle(Z * radial_point, X * circum_dist):
            p += center
            result.add(p)
            if len(result) > result_len:
                result_len += 1
                yield p


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def filled(points):
    """
    Generator function which yields the coordinates necessary to fill the space
    enclosed by the specified *points*.

    This function can be applied to anything that returns a sequence of points.
    For example, to create a filled triangle::

        >>> triangle = [O, 4*X, 4*Z]
        >>> list(filled(lines(triangle)))
        [Vector(x=0, y=0, z=0), Vector(x=0, y=0, z=1), Vector(x=0, y=0, z=2),
         Vector(x=0, y=0, z=3), Vector(x=0, y=0, z=4), Vector(x=1, y=0, z=2),
         Vector(x=1, y=0, z=1), Vector(x=1, y=0, z=0), Vector(x=1, y=0, z=3),
         Vector(x=2, y=0, z=1), Vector(x=2, y=0, z=0), Vector(x=2, y=0, z=2),
         Vector(x=3, y=0, z=1), Vector(x=3, y=0, z=0), Vector(x=4, y=0, z=0)]

    Or to create a filled circle::

        >>> list(filled(circle(O, 4*X)))
        [Vector(x=-4, y=0, z=0), Vector(x=-3, y=-1, z=0), Vector(x=-3, y=-2, z=0),
         Vector(x=-3, y=0, z=0), Vector(x=-3, y=1, z=0), Vector(x=-3, y=2, z=0),
         Vector(x=-2, y=-1, z=0), Vector(x=-2, y=-2, z=0), Vector(x=-2, y=-3, z=0),
         Vector(x=-2, y=0, z=0), Vector(x=-2, y=1, z=0), Vector(x=-2, y=2, z=0),
         Vector(x=-2, y=3, z=0), Vector(x=-1, y=0, z=0), Vector(x=-1, y=-1, z=0),
         Vector(x=-1, y=-2, z=0), Vector(x=-1, y=-3, z=0), Vector(x=-1, y=1, z=0),
         Vector(x=-1, y=2, z=0), Vector(x=-1, y=3, z=0), Vector(x=0, y=-1, z=0),
         Vector(x=0, y=-2, z=0), Vector(x=0, y=-3, z=0), Vector(x=0, y=-4, z=0),
         Vector(x=0, y=0, z=0), Vector(x=0, y=1, z=0), Vector(x=0, y=2, z=0),
         Vector(x=0, y=3, z=0), Vector(x=0, y=4, z=0), Vector(x=1, y=0, z=0),
         Vector(x=1, y=-1, z=0), Vector(x=1, y=-2, z=0), Vector(x=1, y=-3, z=0),
         Vector(x=1, y=1, z=0), Vector(x=1, y=2, z=0), Vector(x=1, y=3, z=0),
         Vector(x=2, y=0, z=0), Vector(x=2, y=-1, z=0), Vector(x=2, y=-2, z=0),
         Vector(x=2, y=-3, z=0), Vector(x=2, y=1, z=0), Vector(x=2, y=2, z=0),
         Vector(x=2, y=3, z=0), Vector(x=3, y=0, z=0), Vector(x=3, y=-1, z=0),
         Vector(x=3, y=-2, z=0), Vector(x=3, y=1, z=0), Vector(x=3, y=2, z=0),
         Vector(x=4, y=0, z=0), Vector(x=4, y=-1, z=0), Vector(x=4, y=1, z=0)]

    To draw the resulting filled object you can simply assign a block to the
    collection of vectors generated (or assign a sequence of blocks of equal
    length if you want the object to have varying block types)::

        >>> world.blocks[filled(lines(triangle))] = Block('stone')

    A simple brute-force algorithm is used that simply generates all the lines
    connecting all specified points. However, duplicate elimination is used to
    ensure that no point within the filled space is yielded twice.

    Note that if you pass the coordinates of a polyhedron which contains holes
    or gaps compared to its convex hull, this function *may* fill those holes
    or gaps (but it will depend on the orientation of the object).
    """
    result = set()
    result_len = 0
    for p, q in pairwise(sorted(points)):
        for l in line(p, q):
            result.add(l)
            if len(result) > result_len:
                result_len += 1
                yield l

