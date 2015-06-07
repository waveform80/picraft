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
import io
import picraft.events
from picraft import World, Vector
try:
    from unittest import mock
except ImportError:
    import mock


def test_events_poll_empty():
    conn = mock.MagicMock()
    conn.transact.return_value = ''
    events = picraft.events.Events(conn)
    assert events.poll() == []
    conn.transact.assert_called_once_with('events.block.hits()')

def test_events_poll_one_hit():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = events.poll()
    assert len(result) == 1
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5
    conn.transact.assert_called_once_with('events.block.hits()')

def test_events_poll_multi_hits():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5|-1,0,0,0,1'
    events = picraft.events.Events(conn)
    result = events.poll()
    assert len(result) == 2
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5
    assert result[1].pos == Vector(-1, 0, 0)
    assert result[1].face == 'y-'
    assert result[1].player.player_id == 1
    conn.transact.assert_called_once_with('events.block.hits()')

def test_events_clear():
    conn = mock.MagicMock()
    events = picraft.events.Events(conn)
    events.clear()
    conn.send.assert_called_once_with('events.clear()')

