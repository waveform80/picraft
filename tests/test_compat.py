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
from picraft.compat import range
try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest


def test_range_init():
    assert range(10).start == 0
    assert range(1, 10).step == 1
    assert range(3, 10, 3) == range(3, 10, 3)
    with pytest.raises(ValueError):
        range(0, 10, 0)
    with pytest.raises(TypeError):
        range(0.0, 10.0, 0.5)

def test_range_equality():
    assert range(10) == range(10)
    assert range(10, 10) == range(1, 1)
    assert range(10, 11) == range(10, 9, -1)
    assert range(0, 10, 3) == range(0, 11, 3)
    assert range(0, 10, 3) != range(0, 13, 3)
    # Yeah ... this one's weird, but it matches Py3 behaviour ...
    assert range(10) != [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_range_len():
    assert len(range(10)) == 10
    assert len(range(10, 10)) == 0
    assert len(range(10)[::-1]) == 10
    assert len(range(3, 10, 3)) == 3

def test_range_bool():
    assert range(10)
    assert not range(10, 10)
    assert range(3, 10, 3)

def test_range_index():
    assert range(10).index(0) == 0
    assert range(10).index(9) == 9
    assert range(3, 10, 3).index(3) == 0
    assert range(3, 10, 3).index(9) == 2
    assert range(3, 10, 3)[::-1].index(9) == 0
    with pytest.raises(ValueError):
        range(10).index(10)

def test_range_count():
    assert range(10).count(0) == 1
    assert range(10).count(10) == 0
    assert range(3, 10, 3).count(4) == 0
    assert range(3, 10, 3).count(6) == 1

def test_range_contains():
    assert 0 in range(10)
    assert 10 not in range(10)
    assert 3 in range(3, 10, 3)
    assert 3 in range(3, 10, 3)[::-1]
    assert 0 not in range(3, 10, 3)

def test_range_iter():
    r = range(10)
    for i, v in enumerate(r):
        assert r[i] == v
    r = range(3, 10, 3)
    for i, v in enumerate(r):
        assert r[i] == v

def test_range_reversed():
    r = range(10)
    for i, v in enumerate(reversed(r)):
        assert r[::-1][i] == v
    r = range(3, 10, 3)
    for i, v in enumerate(reversed(r)):
        assert r[::-1][i] == v

def test_range_get():
    r = range(10)
    t = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for v1, v2 in zip_longest(r, t):
        assert v1 == v2
    r = range(3, 10, 3)
    t = [3, 6, 9]
    for v1, v2 in zip_longest(r, t):
        assert v1 == v2
    with pytest.raises(IndexError):
        range(10)[10]
    with pytest.raises(IndexError):
        range(10)[-11]

def test_range_get_slice():
    assert range(10)[1:] == range(1, 10)
    assert range(10)[-5:] == range(5, 10)
    assert range(10)[20:] == range(1, 1)
    assert range(10)[:5] == range(5)
    assert range(10)[:-2] == range(8)
    assert range(10)[:20] == range(10)
    assert range(10)[1:-1] == range(1, 9)
    assert range(10)[::-1] == range(9, -1, -1)
    assert range(10)[2::-1] == range(2, -1, -1)
    assert range(3, 10, 3)[1:] == range(6, 12, 3)
    assert range(3, 10, 3)[::-1] == range(9, 0, -3)
    assert range(3, 10, 3)[2::-1] == range(9, 0, -3)
    assert range(0, 10, 3)[:-3:-1] == range(9, 3, -3)
    with pytest.raises(ValueError):
        range(10)[::0]
