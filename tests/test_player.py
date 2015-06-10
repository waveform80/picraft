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
import picraft.player
from picraft import HostPlayer, Player, Vector, NoResponse, NotSupported
try:
    from unittest import mock
except ImportError:
    import mock


def test_players_len():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert len(players) == 3

def test_players_contains():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert 1 in players
    assert 4 not in players

def test_players_iter():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert len(list(iter(players))) == 3

def test_players_get():
    conn = mock.MagicMock()
    def mock_transact(s):
        if s == 'world.getPlayerIds()':
            return '1|2|3'
        elif s == 'world.getPlayerId(foo)':
            return '1'
        else:
            raise NoResponse()
    conn.transact.side_effect = mock_transact
    conn.server_version = 'raspberry-juice'
    players = picraft.player.Players(conn)
    assert players[2].player_id == 2
    with pytest.raises(KeyError):
        players[4]
    assert players['foo'].player_id == 1
    with pytest.raises(KeyError):
        players['bar']

def test_players_keys():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert set(players.keys()) == {1, 2, 3}

def test_players_values():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert {p.player_id for p in players.values()} == {1, 2, 3}

def test_players_items():
    conn = mock.MagicMock()
    conn.transact.return_value = '1|2|3'
    players = picraft.player.Players(conn)
    assert {(k, v.player_id) for (k, v) in players.items()} == {(1, 1), (2, 2), (3, 3)}

def test_player_pos():
    conn = mock.MagicMock()
    conn.transact.return_value = '0.0,0.0,0.0'
    assert Player(conn, 1).pos == Vector(0.0, 0.0, 0.0)
    conn.transact.assert_called_once_with('entity.getPos(1)')
    Player(conn, 1).pos = Vector(1, 2, 3)
    conn.send.assert_called_once_with('entity.setPos(1,1,2,3)')

def test_player_tile_pos():
    conn = mock.MagicMock()
    conn.transact.return_value = '0,0,0'
    assert Player(conn, 1).tile_pos == Vector(0, 0, 0)
    conn.transact.assert_called_once_with('entity.getTile(1)')
    Player(conn, 1).tile_pos = Vector(1, 2, 3)
    conn.send.assert_called_once_with('entity.setTile(1,1,2,3)')

def test_player_heading():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '90.0'
    assert Player(conn, 1).heading == 90.0
    conn.transact.assert_called_once_with('entity.getRotation(1)')

def test_player_pitch():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '10.0'
    assert Player(conn, 1).pitch == 10.0
    conn.transact.assert_called_once_with('entity.getPitch(1)')

def test_player_direction():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '1.0,0.0,0.0'
    assert Player(conn, 1).direction == Vector(1.0, 0.0, 0.0)
    conn.transact.assert_called_once_with('entity.getDirection(1)')

def test_player_mcpi():
    conn = mock.MagicMock()
    conn.server_version = 'minecraft-pi'
    with pytest.raises(NotSupported):
        Player(conn, 1).heading
    with pytest.raises(NotSupported):
        Player(conn, 1).pitch
    with pytest.raises(NotSupported):
        Player(conn, 1).direction

def test_host_player_autojump():
    conn = mock.MagicMock()
    conn.server_version = 'minecraft-pi'
    with pytest.raises(AttributeError):
        HostPlayer(conn).autojump
    HostPlayer(conn).autojump = True
    conn.send.assert_called_once_with('player.setting(autojump,1)')
    conn.server_version = 'raspberry-juice'
    with pytest.raises(NotSupported):
        HostPlayer(conn).autojump = True

def test_host_player_pos():
    conn = mock.MagicMock()
    conn.transact.return_value = '0.0,0.0,0.0'
    assert HostPlayer(conn).pos == Vector(0.0, 0.0, 0.0)
    conn.transact.assert_called_once_with('player.getPos()')
    HostPlayer(conn).pos = Vector(1, 2, 3)
    conn.send.assert_called_once_with('player.setPos(1,2,3)')

def test_host_player_tile_pos():
    conn = mock.MagicMock()
    conn.transact.return_value = '0,0,0'
    assert HostPlayer(conn).tile_pos == Vector(0, 0, 0)
    conn.transact.assert_called_once_with('player.getTile()')
    HostPlayer(conn).tile_pos = Vector(1, 2, 3)
    conn.send.assert_called_once_with('player.setTile(1,2,3)')

def test_host_player_heading():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '90.0'
    assert HostPlayer(conn).heading == 90.0
    conn.transact.assert_called_once_with('player.getRotation()')

def test_host_player_pitch():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '10.0'
    assert HostPlayer(conn).pitch == 10.0
    conn.transact.assert_called_once_with('player.getPitch()')

def test_host_player_direction():
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '1.0,0.0,0.0'
    assert HostPlayer(conn).direction == Vector(1.0, 0.0, 0.0)
    conn.transact.assert_called_once_with('player.getDirection()')

