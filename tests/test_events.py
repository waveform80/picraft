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


import pytest
import io
import re
import picraft.events
import threading
import time
from picraft import (
    World,
    Vector,
    BlockHitEvent,
    PlayerPosEvent,
    ChatPostEvent,
    IdleEvent,
    ConnectionClosed,
    )
try:
    from unittest import mock
except ImportError:
    import mock


def test_events_poll_gap_attr():
    conn = mock.MagicMock()
    events = picraft.events.Events(conn)
    events.poll_gap = 1
    assert events.poll_gap == 1.0
    events.poll_gap = 0.1
    assert events.poll_gap == 0.1

def test_events_track_players_attr():
    with mock.patch('picraft.events.Player'):
        conn = mock.MagicMock()
        events = picraft.events.Events(conn)
        events.track_players = 1
        assert set(events.track_players) == {1}
        events.track_players = {1, 2, 3}
        assert set(events.track_players) == {1, 2, 3}
        with pytest.raises(ValueError):
            events.track_players = 1.0

def test_events_include_idle_attr():
    conn = mock.MagicMock()
    events = picraft.events.Events(conn)
    events.include_idle = False
    assert not events.include_idle
    events.include_idle = 1
    assert events.include_idle

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
    assert isinstance(result[0], BlockHitEvent)
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5
    conn.transact.assert_called_once_with('events.block.hits()')

def test_events_poll_one_move():
    conn = mock.MagicMock()
    conn.transact.side_effect = ['1.0,1.0,1.0', '1.1,1.0,1.0', '']
    events = picraft.events.Events(conn)
    events.track_players = {1}
    result = events.poll()
    assert len(result) == 1
    assert isinstance(result[0], PlayerPosEvent)
    assert result[0].old_pos == Vector(1.0, 1.0, 1.0)
    assert result[0].new_pos == Vector(1.1, 1.0, 1.0)
    assert result[0].player.player_id == 1
    conn.transact.assert_has_calls([
        mock.call('entity.getPos(1)'),
        mock.call('entity.getPos(1)'),
        mock.call('events.block.hits()'),
        ])

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

def test_events_poll_idle():
    conn = mock.MagicMock()
    conn.transact.return_value = ''
    events = picraft.events.Events(conn)
    events.include_idle = True
    result = events.poll()
    assert len(result) == 1
    assert isinstance(result[0], IdleEvent)

def test_events_post_message():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,Hello world!']
    events = picraft.events.Events(conn)
    result = events.poll()
    assert len(result) == 1
    assert result[0].message == 'Hello world!'
    assert result[0].player.player_id == 1
    conn.transact.assert_any_call('events.block.hits()')
    conn.transact.assert_any_call('events.chat.posts()')

def test_events_clear():
    conn = mock.MagicMock()
    events = picraft.events.Events(conn)
    events.clear()
    conn.send.assert_called_once_with('events.clear()')

def test_events_idle_decorator():
    conn = mock.MagicMock()
    conn.transact.return_value = ''
    events = picraft.events.Events(conn)
    events.include_idle = True
    result = []
    @events.on_idle()
    def handler(event):
        result.append(1)
    events.process()
    assert result

def test_events_pos_decorator():
    conn = mock.MagicMock()
    conn.transact.side_effect = ['1.0,1.0,1.0', '1.1,1.0,1.0', '']
    events = picraft.events.Events(conn)
    events.track_players = {1}
    result = []
    @events.on_player_pos()
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].old_pos == Vector(1.0, 1.0, 1.0)
    assert result[0].new_pos == Vector(1.1, 1.0, 1.0)
    assert result[0].player.player_id == 1

def test_events_hit_decorator():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit()
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5

def test_events_chat_decorator():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,Hello world!']
    events = picraft.events.Events(conn)
    result = []
    @events.on_chat_post()
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].message == 'Hello world!'
    assert result[0].player.player_id == 1

def test_events_multi_thread_handler():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5|-1,0,0,0,1'
    events = picraft.events.Events(conn)
    result = []
    lock = threading.Lock()
    @events.on_block_hit(thread=True)
    def handler(event):
        with lock:
            result.append(event)
    events.process()
    # The handler is threaded so there's no guarantee the result has been
    # filled by this point. Hence, we wait up to two seconds for that to
    # happen, with a small wait between acquiring locks to avoid lock
    # starvation in the background threads.
    start = time.time()
    while time.time() - start < 2:
        with lock:
            if len(result) == 2:
                if result[0].pos != Vector(1, 2, 3):
                    result[0], result[1] = result[1], result[0]
                assert result[0].pos == Vector(1, 2, 3)
                assert result[0].face == 'x-'
                assert result[0].player.player_id == 5
                assert result[1].pos == Vector(-1, 0, 0)
                assert result[1].face == 'y-'
                assert result[1].player.player_id == 1
                break
        time.sleep(0.1)

def test_events_multi_thread_single_exec_handler():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5|-1,0,0,0,1'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(thread=True, multi=False)
    def handler(event):
        result.append(event)
        # This delay should cause the second event to be thrown away
        time.sleep(0.2)
    events.process()
    time.sleep(0.5)
    assert len(result) == 1
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5

def test_events_pos_handler_filter_one():
    conn = mock.MagicMock()
    conn.transact.side_effect = ['1.0,1.0,1.0', '1.1,1.0,1.0', '']
    events = picraft.events.Events(conn)
    events.track_players = {1}
    result = []
    @events.on_player_pos(old_pos=Vector(2, 0, 0))
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 0

def test_events_pos_handler_filter_many():
    conn = mock.MagicMock()
    conn.transact.side_effect = ['1.0,1.0,1.0', '1.1,1.0,1.0', '']
    events = picraft.events.Events(conn)
    events.track_players = {1}
    result = []
    @events.on_player_pos(old_pos=[Vector(0, 0, 0), Vector(1, 0, 0), Vector(1, 1, 1)])
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].old_pos == Vector(1.0, 1.0, 1.0)
    assert result[0].new_pos == Vector(1.1, 1.0, 1.0)
    assert result[0].player.player_id == 1

def test_events_pos_handler_filter_bad():
    conn = mock.MagicMock()
    conn.transact.side_effect = ['1.0,1.0,1.0', '1.1,1.0,1.0', '']
    events = picraft.events.Events(conn)
    events.track_players = {1}
    result = []
    @events.on_player_pos(old_pos=1)
    def handler(event):
        result.append(event)
    with pytest.raises(TypeError):
        events.process()

def test_events_hit_handler_filter_one():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(pos=Vector(1, 2, 3), face='x-')
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5

def test_events_hit_handler_filter_many():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(pos=[Vector(0, 0, 0), Vector(1, 2, 3)], face=['x+', 'x-'])
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].pos == Vector(1, 2, 3)
    assert result[0].face == 'x-'
    assert result[0].player.player_id == 5

def test_events_hit_handler_filter_bad1():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(pos=1, face=['x+', 'x-'])
    def handler(event):
        result.append(event)
    with pytest.raises(TypeError):
        events.process()

def test_events_hit_handler_filter_bad2():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(pos=Vector(1, 2, 3), face=False)
    def handler(event):
        result.append(event)
    with pytest.raises(TypeError):
        events.process()

def test_events_hit_handler_filter_face_bytes():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,2,3,4,5'
    events = picraft.events.Events(conn)
    result = []
    @events.on_block_hit(pos=Vector(1, 2, 3), face=b'y-')
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 0

def test_events_chat_handler_filter_message():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,teleport']
    events = picraft.events.Events(conn)
    result = []
    @events.on_chat_post(message='teleport')
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].message == 'teleport'
    assert result[0].player.player_id == 1

def test_events_chat_handler_filter_message_re():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,teleport 0,0,0']
    events = picraft.events.Events(conn)
    result = []
    @events.on_chat_post(message=re.compile(r'teleport \d+,\d+,\d+'))
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].message == 'teleport 0,0,0'
    assert result[0].player.player_id == 1

def test_events_chat_handler_filter_message_bytes():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,teleport']
    events = picraft.events.Events(conn)
    result = []
    @events.on_chat_post(message=b'teleport')
    def handler(event):
        result.append(event)
    events.process()
    assert len(result) == 1
    assert result[0].message == 'teleport'
    assert result[0].player.player_id == 1

def test_events_chat_handler_filter_message_bad():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.side_effect = ['', '1,teleport']
    events = picraft.events.Events(conn)
    result = []
    @events.on_chat_post(message=1)
    def handler(event):
        result.append(event)
    with pytest.raises(TypeError):
        events.process()

def test_events_main_loop():
    conn = mock.MagicMock()
    conn.transact.return_value = ''
    events = picraft.events.Events(conn)
    events.include_idle = True
    @events.on_idle()
    def handler(event):
        conn.transact.side_effect=ConnectionClosed()
    main_loop_thread = threading.Thread(target=events.main_loop)
    main_loop_thread.start()
    main_loop_thread.join(timeout=1)
    assert not main_loop_thread.is_alive()

