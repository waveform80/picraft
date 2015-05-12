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
from picraft import Vector

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
    assert Vector(1, 2, 3) / Vector(2, 2, 2) == Vector(0.5, 1, 1.5)
    assert Vector(1, 2, 3) / 2 == Vector(0.5, 1, 1.5)
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
    assert Vector(1, 2, 3) ** 2 == Vector(1, 4, 9)
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

