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


import pytest
import math
from .conftest import fp_equal, fp_vectors_equal
from picraft import Vector, vector_range, O, X, Y, Z
from picraft.vector import rmod, rdiv
from picraft.compat import range


def test_vector_init():
    assert Vector() == (0, 0, 0)
    assert Vector(1) == (1, 0, 0)
    assert Vector(1, 2, 3) == (1, 2, 3)
    assert Vector(z=3, y=2, x=1) == (1, 2, 3)

def test_vector_from_string():
    assert Vector.from_string('1,2,3') == Vector(1, 2, 3)
    assert Vector.from_string('1, 2, 3') == Vector(1, 2, 3)
    with pytest.raises(ValueError):
        Vector.from_string('1')
    with pytest.raises(ValueError):
        Vector.from_string('(1,2,3)')

def test_vector_str():
    assert str(Vector()) == '0,0,0'
    assert str(Vector(1, 2, 3)) == '1,2,3'
    assert str(Vector(0.1, 0.2, 0.3)) == '0.1,0.2,0.3'

def test_vector_add():
    assert Vector() + Vector(1, 2, 3) == Vector(1,2, 3)
    assert Vector() + 1 == Vector(1, 1, 1)
    assert 1 + Vector() == Vector(1, 1, 1)

def test_vector_sub():
    assert Vector(1, 2, 3) - Vector(1, 1, 1) == Vector(0, 1, 2)
    assert Vector(1, 2, 3) - 1 == Vector(0, 1, 2)
    with pytest.raises(TypeError):
        1 - Vector()

def test_vector_mul():
    assert Vector(1, 2, 3) * Vector(3, 3, 3) == Vector(3, 6, 9)
    assert Vector(1, 2, 3) * 3 == Vector(3, 6, 9)
    assert 3 * Vector(1, 2, 3) == Vector(3, 6, 9)

def test_vector_truediv():
    assert fp_vectors_equal(Vector(1, 2, 3) / Vector(2, 2, 2), Vector(0.5, 1, 1.5))
    assert fp_vectors_equal(Vector(1, 2, 3) / 2, Vector(0.5, 1, 1.5))
    with pytest.raises(TypeError):
        2 / Vector(1, 2, 3)

def test_vector_floordiv():
    assert Vector(1, 2, 3) // Vector(2, 2, 2) == Vector(0, 1, 1)
    assert Vector(1, 2, 3) // 2 == Vector(0, 1, 1)
    with pytest.raises(TypeError):
        2 // Vector(1, 2, 3)

def test_vector_mod():
    assert Vector(1, 3, 9) % Vector(3, 3, 3) == Vector(1, 0, 0)
    assert Vector(2, 3, 4) % 2 == Vector(0, 1, 0)
    with pytest.raises(TypeError):
        2 % Vector(1, 1, 1)

def test_vector_pow():
    assert Vector(1, 2, 3) ** Vector(2, 2, 2) == Vector(1, 4, 9)
    assert Vector(1, 2, 3) ** Vector(2, 2, 2) == Vector(1, 4, 9)
    assert pow(Vector(1, 2, 3), Vector(2, 2, 2), Vector(5, 5, 5)) == Vector(1, 4, 4)
    assert Vector(1, 2, 3) ** 2 == Vector(1, 4, 9)
    assert pow(Vector(1, 2, 3), 2, 5) == Vector(1, 4, 4)
    with pytest.raises(TypeError):
        2 ** Vector(1, 2, 3)

def test_vector_lshift():
    assert Vector(1, 2, 3) << Vector(1, 2, 3) == Vector(2, 8, 24)
    assert Vector(1, 2, 3) << 1 == Vector(2, 4, 6)
    with pytest.raises(TypeError):
        2 << Vector(1, 2, 3)

def test_vector_rshift():
    assert Vector(2, 8, 16) >> Vector(0, 1, 2) == Vector(2, 4, 4)
    assert Vector(2, 8, 16) >> 1 == Vector(1, 4, 8)
    with pytest.raises(TypeError):
        2 >> Vector(1, 1, 1)

def test_vector_and():
    assert Vector(1, 2, 3) & Vector(1, 1, 1) == Vector(1, 0, 1)
    assert Vector(4, 4, 4) & Vector(0x7fff, 0, 0) == Vector(4, 0, 0)
    assert Vector(1, 2, 3) & 1 == Vector(1, 0, 1)

def test_vector_xor():
    assert Vector(1, 2, 3) ^ Vector(1, 1, 1) == Vector(0, 3, 2)
    assert Vector(4, 4, 4) ^ Vector(4, 4, 4) == Vector(0, 0, 0)
    assert Vector(1, 2, 3) ^ 1 == Vector(0, 3, 2)

def test_vector_or():
    assert Vector(1, 2, 3) | Vector(1, 1, 1) == Vector(1, 3, 3)
    assert Vector(4, 4, 4) | Vector(1, 2, 3) == Vector(5, 6, 7)
    assert Vector(1, 2, 3) | 1 == Vector(1, 3, 3)

def test_vector_neg():
    assert -Vector(1, 1, 1) == Vector(-1, -1, -1)

def test_vector_pos():
    assert +Vector(1, 1, 1) == Vector(1, 1, 1)

def test_vector_abs():
    assert abs(Vector(-1, 1, -2)) == Vector(1, 1, 2)
    assert abs(Vector(0, 1, 2)) == Vector(0, 1, 2)

def test_vector_bool():
    assert Vector(1, 0, 0)
    assert Vector(0, 1, 0)
    assert Vector(0, 0, 1)
    assert not Vector()

def test_vector_dot():
    assert Vector(1, 1, 1).dot(Vector()) == 0
    assert Vector(1, 2, 3).dot(Vector(1, 1, 1)) == 6
    assert Vector(1, 2, 3).dot(Vector(0, 0, 2)) == 6

def test_vector_cross():
    assert Vector(x=1).cross(Vector(x=1)) == Vector()
    assert Vector(y=1).cross(Vector(y=-1)) == Vector()
    assert Vector(z=1).cross(Vector(z=1)) == Vector()
    assert Vector(x=1).cross(Vector(y=1)) == Vector(z=1)
    assert Vector(x=1).cross(Vector(y=-1)) == Vector(z=-1)

def test_vector_distance_to():
    assert Vector().distance_to(Vector()) == 0.0
    assert Vector(x=1).distance_to(Vector(x=2)) == 1.0
    assert Vector(x=1).distance_to(Vector(2, 1, 0)) == 2 ** 0.5

def test_vector_magnitude():
    assert Vector().magnitude == 0
    assert Vector(2, 4, 4).magnitude == 6

def test_vector_unit():
    assert Vector(x=1).unit == Vector(1, 0, 0)
    assert Vector().unit == Vector()
    assert Vector(2, 4, 4).unit == Vector(1/3, 2/3, 2/3)

def test_vector_replace():
    assert Vector().replace(x=1) == Vector(1, 0, 0)
    assert Vector(1, 2, 3).replace() == Vector(1, 2, 3)
    assert Vector(1, 2, 3).replace(2, 4, 6) == Vector(2, 4, 6)
    assert Vector(1, 2, 3).replace(z=-1) == Vector(1, 2, -1)

def test_vector_trunc():
    assert math.trunc(Vector(1, 2, 3)) == Vector(1, 2, 3)
    assert math.trunc(Vector(1.1, 2.5, -1.1)) == Vector(1, 2, -1)
    assert math.trunc(Vector(1.9, 0.0, -1.9)) == Vector(1, 0, -1)

def test_vector_floor():
    assert Vector(1, 2, 3).floor() == Vector(1, 2, 3)
    assert Vector(1.1, 2.5, -1.1).floor() == Vector(1, 2, -2)
    assert Vector(1.9, 0.0, -1.9).floor() == Vector(1, 0, -2)

def test_vector_ceil():
    assert Vector(1, 2, 3).ceil() == Vector(1, 2, 3)
    assert Vector(1.1, 2.5, -1.1).ceil() == Vector(2, 3, -1)
    assert Vector(1.9, 0.0, -1.9).ceil() == Vector(2, 0, -1)

def test_vector_round():
    assert fp_vectors_equal(Vector(1, 2, 3).round(), Vector(1, 2, 3))
    assert fp_vectors_equal(Vector(1.1, 3.5, -1.1).round(), Vector(1, 4, -1))
    assert fp_vectors_equal(Vector(1.9, 0.0, -1.9).round(), Vector(2, 0, -2))
    assert fp_vectors_equal(Vector(1.9, 0.0, -1.9).round(1), Vector(1.9, 0.0, -1.9))
    assert fp_vectors_equal(Vector(1.9, 0.0, -1.9).round(-1), Vector(0, 0, 0))

def test_vector_angle_between():
    assert fp_equal(X.angle_between(Y), 90.0)
    assert fp_equal(Y.angle_between(Z), 90.0)
    assert fp_equal((X + Y).angle_between(X), 45.0)

def test_vector_project():
    assert fp_equal(X.project(X), 1.0)
    assert fp_equal(X.project(Y), 0.0)
    assert fp_equal(X.project(Z), 0.0)
    assert fp_equal(Vector(1, 2, 3).project(2 * Y), 2.0)
    assert fp_equal(Vector(3, 4, 5).project(Vector(3, 4, 0)), 5.0)

def test_vector_rotate():
    assert fp_vectors_equal(X.rotate(90, about=X), X)
    assert fp_vectors_equal(X.rotate(90, about=Y), -Z)
    assert fp_vectors_equal(X.rotate(90, about=Z), Y)
    assert fp_vectors_equal(X.rotate(90, about=-X), X)
    assert fp_vectors_equal(X.rotate(90, about=-Y), Z)
    assert fp_vectors_equal(X.rotate(90, about=-Z), -Y)
    assert fp_vectors_equal(X.rotate(180, about=X + Y), Y)
    assert fp_vectors_equal(O.rotate(180, about=Y, origin=Z), 2*Z)

def test_vector_range_init():
    v = vector_range(Vector() + 2)
    assert v.start == Vector()
    assert v.stop == Vector(2, 2, 2)
    assert v.step == Vector(1, 1, 1)
    with pytest.raises(TypeError):
        vector_range(Vector(0.0, 0.0, 0.0), step=Vector(0.5, 0.5, 1.0))

def test_vector_range_start():
    assert vector_range(Vector() + 1).start == Vector()
    assert vector_range(Vector(), Vector() + 1).start == Vector()
    assert vector_range(Vector(1, 0, 1), Vector() + 1).start == Vector(1, 0, 1)

def test_vector_range_stop():
    assert vector_range(Vector() + 1).stop == Vector(1, 1, 1)
    assert vector_range(Vector(1, 1, 0)).stop == Vector(1, 1, 0)
    assert vector_range(Vector(1, 0, 1), Vector() + 1).stop == Vector(1, 1, 1)

def test_vector_range_step():
    assert vector_range(Vector() + 1, step=Vector() + 2).step == Vector(2, 2, 2)
    assert vector_range(Vector(), Vector() + 1, Vector() + 1).step == Vector(1, 1, 1)
    with pytest.raises(ValueError):
        vector_range(Vector() + 1, step=Vector(1, 1, 0))

def test_vector_range_order():
    assert vector_range(Vector() + 1).order == 'zxy'
    assert vector_range(Vector() + 1, order='xyz').order == 'xyz'
    with pytest.raises(ValueError):
        vector_range(Vector() + 2, order='abc')

def test_vector_range_index():
    assert vector_range(Vector() + 2).index(Vector()) == 0
    assert vector_range(Vector() + 2)[:Vector() - 1].index(Vector()) == 0
    assert vector_range(Vector() + 2).index(Vector(1, 1, 1)) == 7
    assert vector_range(Vector() + 2)[Vector(z=1):].index(Vector(1, 1, 1)) == 3
    assert vector_range(Vector() + 2, order='xyz').index(Vector(1, 0, 0)) == 1
    assert vector_range(Vector() + 2, order='zxy').index(Vector(1, 0, 0)) == 2
    assert vector_range(Vector() + 2, order='zyx').index(Vector(1, 0, 0)) == 4
    with pytest.raises(ValueError):
        vector_range(Vector() + 2).index(Vector(2, 2, 2))

def test_vector_range_contains():
    assert Vector() in vector_range(Vector() + 2)
    assert Vector(1, 1, 1) in vector_range(Vector() + 2)
    assert Vector(x=1) in vector_range(Vector() + 2, order='xyz')
    assert Vector() + 2 not in vector_range(Vector() + 2)

def test_vector_range_count():
    assert vector_range(Vector() + 2).count(Vector()) == 1
    assert vector_range(Vector() + 2).count(Vector(1, 1, 1)) == 1
    assert vector_range(Vector() + 2, order='xyz').count(Vector(1, 0, 0)) == 1
    assert vector_range(Vector() + 2).count(Vector(2, 2, 2)) == 0

def test_vector_range_len():
    assert len(vector_range(Vector())) == 0
    assert len(vector_range(Vector() + 1)) == 1
    assert len(vector_range(Vector() + 2)) == 8
    assert len(vector_range(Vector() + 3)) == 27

def test_vector_range_ordering():
    assert vector_range(Vector() + 2, order='xyz') == vector_range(Vector(2, 2, 2), order='xyz')
    assert vector_range(Vector() + 2, order='xyz') == list(vector_range(Vector(2, 2, 2), order='xyz'))

    assert vector_range(Vector() + 2, order='zxy') <= vector_range(Vector() + 2, order='xyz')
    assert vector_range(Vector() + 2, order='zxy') <= vector_range(Vector() + 2, order='zxy')
    assert vector_range(Vector() + 2, order='zxy') < vector_range(Vector() + 2, order='xyz')
    assert not (vector_range(Vector() + 2, order='zxy') < vector_range(Vector() + 2, order='zxy'))

    assert vector_range(Vector() + 2, order='xyz') > vector_range(Vector() + 2, order='zxy')
    assert vector_range(Vector() + 2, order='xyz') >= vector_range(Vector() + 2, order='zxy')
    assert vector_range(Vector() + 2, order='xyz') != vector_range(Vector() + 2, order='zxy')

    assert vector_range(Vector() + 2, order='xyz') == [
            Vector(0, 0, 0), Vector(1, 0, 0), Vector(0, 1, 0), Vector(1, 1, 0),
            Vector(0, 0, 1), Vector(1, 0, 1), Vector(0, 1, 1), Vector(1, 1, 1),
            ]
    assert vector_range(Vector() + 2, order='zxy') == [
            Vector(0, 0, 0), Vector(0, 0, 1), Vector(1, 0, 0), Vector(1, 0, 1),
            Vector(0, 1, 0), Vector(0, 1, 1), Vector(1, 1, 0), Vector(1, 1, 1),
            ]
    assert vector_range(Vector() + 2, order='zyx') == [
            Vector(0, 0, 0), Vector(0, 0, 1), Vector(0, 1, 0), Vector(0, 1, 1),
            Vector(1, 0, 0), Vector(1, 0, 1), Vector(1, 1, 0), Vector(1, 1, 1),
            ]

    assert iter(vector_range(Vector() + 2, order='zxy')) < vector_range(Vector() + 2, order='xyz')
    assert iter(vector_range(Vector() + 2, order='zxy')) <= vector_range(Vector() + 2, order='xyz')
    assert iter(vector_range(Vector() + 2, order='xyz')) > vector_range(Vector() + 2, order='zxy')
    assert iter(vector_range(Vector() + 2, order='xyz')) >= vector_range(Vector() + 2, order='zxy')
    assert iter(vector_range(Vector() + 2, order='xyz')) != vector_range(Vector() + 2, order='zxy')

def test_vector_range_reversed():
    assert list(reversed(vector_range(Vector() + 2))) == list(reversed(list(vector_range(Vector() + 2))))
    assert list(reversed(vector_range(Vector() + 2, order='xyz'))) == vector_range(Vector() + 1, Vector() - 1, Vector() - 1, order='xyz')
    assert list(reversed(vector_range(Vector() + 2, order='xyz'))) == vector_range(Vector() + 2, order='xyz')[::Vector() - 1]

def test_vector_range_bool():
    assert not vector_range(Vector())
    assert vector_range(Vector() + 1)
    assert not vector_range(Vector() + 1)[Vector() + 1:]

def test_vector_range_getitem():
    v = vector_range(Vector() + 2, order='xyz')
    assert v[0] == Vector()
    assert v[1] == Vector(1, 0, 0)
    assert v[7] == Vector(1, 1, 1)
    assert v[7] == v[-1]
    assert v[6] == v[-2]
    assert v[0] == v[-8]
    assert v[Vector()] == Vector()
    assert v[Vector(1, 0, 0)] == Vector(1, 0, 0)
    assert v[Vector() - 1] == Vector(1, 1, 1)
    with pytest.raises(IndexError):
        v[8]
    with pytest.raises(IndexError):
        v[-9]
    with pytest.raises(IndexError):
        v[Vector(2, 1, 1)]

def test_vector_getslice():
    v = vector_range(Vector() + 2, order='xyz')
    assert v[Vector(1, 0, 0):] == vector_range(Vector(x=1), Vector() + 2, order='xyz')
    assert v[:Vector(1, None, None)] == vector_range(Vector(1, 2, 2), order='xyz')
    with pytest.raises(ValueError):
        v[1:]
    with pytest.raises(ValueError):
        v[::Vector(1, 1, 0)]

def test_vector_coverage():
    # Miscellaneous tests purely for the sake of coverage
    assert rmod(3, 3, range(10)) == set()
    assert rmod(3, 2, []) == set()
    with pytest.raises(ValueError):
        rmod(0, 1, range(10))
    with pytest.raises(ValueError):
        rdiv(0, 1)

