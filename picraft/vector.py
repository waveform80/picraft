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
from collections import namedtuple


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


def vector_range(start, stop=None, step=Vector(1, 1, 1), order='xyz'):
    if stop is None:
        stop = start
        start = Vector()
    if order not in ('xyz', 'xzy', 'zxy', 'yxz', 'yzx', 'zyx'):
        raise ValueError('invalid order: %s' % order)
    order = ''.join(reversed(order))
    irange, jrange, krange = [
        range(getattr(start, axis), getattr(stop, axis), getattr(step, axis))
        for axis in order
        ]
    xindex, yindex, zindex = [
        order.index(axis)
        for axis in 'xyz'
        ]
    for i in irange:
        for j in jrange:
            for k in krange:
                v = (i, j, k)
                yield Vector(v[xindex], v[yindex], v[zindex])

