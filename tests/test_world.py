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
import picraft.world
import picraft.block
import picraft.player
import picraft.events
from picraft import World, Vector, vector_range, Connection, NotSupported
try:
    from unittest import mock
except ImportError:
    import mock


def test_world_init():
    with mock.patch('picraft.world.Connection') as c:
        World()
        c.assert_called_once_with('localhost', 4711, 0.2, False)

def test_world_objects():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        assert w.connection is c()
        assert isinstance(w.players, picraft.player.Players)
        assert isinstance(w.player, picraft.player.HostPlayer)
        assert isinstance(w.blocks, picraft.block.Blocks)
        assert isinstance(w.height, picraft.world.WorldHeight)
        assert isinstance(w.camera, picraft.world.Camera)
        assert isinstance(w.checkpoint, picraft.world.Checkpoint)
        assert isinstance(w.events, picraft.events.Events)

def test_world_say():
    with mock.patch('picraft.world.Connection') as c:
        World().say('Hello world!')
        c().send.assert_called_once_with('chat.post(Hello world!)')
        c().send.reset_mock()
        World().say('Hello\nworld!')
        c().send.assert_any_call('chat.post(Hello)')
        c().send.assert_any_call('chat.post(world!)')

def test_world_context():
    with mock.patch('picraft.world.Connection') as c:
        with World():
            pass
        c().close.assert_called_once_with()

def test_world_immutable():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        with pytest.raises(AttributeError):
            w.immutable
        c().server_version = 'minecraft-pi'
        w.immutable = False
        c().send.assert_called_once_with('world.setting(world_immutable,0)')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            w.immutable = False

def test_world_nametags():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        with pytest.raises(AttributeError):
            w.nametags_visible
        c().server_version = 'minecraft-pi'
        w.nametags_visible = False
        c().send.assert_called_once_with('world.setting(nametags_visible,0)')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            w.nametags_visible = False

def test_world_height_get():
    with mock.patch('picraft.world.Connection') as c:
        World().height[Vector(1, 2, 3)]
        c().transact.assert_called_once_with('world.getHeight(1,3)')
        c().transact.reset_mock()
        v_from = Vector(1, 2, 3)
        v_to = Vector(2, 3, 5)
        World().height[v_from:v_to]
        for v in vector_range(v_from, v_to):
            c().transact.assert_any_call('world.getHeight(%d,%d)' % (v.x, v.z))

def test_checkpoint_save():
    with mock.patch('picraft.world.Connection') as c:
        c().server_version = 'minecraft-pi'
        World().checkpoint.save()
        c().send.assert_called_once_with('world.checkpoint.save()')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            World().checkpoint.save()

def test_checkpoint_restore():
    with mock.patch('picraft.world.Connection') as c:
        c().server_version = 'minecraft-pi'
        World().checkpoint.restore()
        c().send.assert_called_once_with('world.checkpoint.restore()')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            World().checkpoint.restore()

def test_checkpoint_context():
    with mock.patch('picraft.world.Connection') as c:
        c().server_version = 'minecraft-pi'
        with World().checkpoint:
            pass
        c().send.assert_called_with('world.checkpoint.save()')
        try:
            with World().checkpoint:
                c().send.assert_called_with('world.checkpoint.save()')
                raise ValueError()
        except ValueError:
            c().send.assert_called_with('world.checkpoint.restore()')

def test_camera_pos():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        with pytest.raises(AttributeError):
            w.camera.pos
        c().server_version = 'minecraft-pi'
        w.camera.pos = Vector(1, 2, 3)
        assert c().send.mock_calls == [
                mock.call('camera.mode.setFixed()'),
                mock.call('camera.setPos(1,2,3)'),
                ]
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            w.camera.pos = Vector(1, 2, 3)

def test_camera_1st_person():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        c().transact.return_value = '1|2|3'
        c().server_version = 'minecraft-pi'
        w.camera.first_person(w.player)
        c().send.assert_called_with('camera.mode.setNormal()')
        w.camera.first_person(w.players[3])
        c().send.assert_called_with('camera.mode.setNormal(3)')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            w.camera.first_person(w.player)

def test_camera_3rd_person():
    with mock.patch('picraft.world.Connection') as c:
        w = World()
        c().transact.return_value = '1|2|3'
        c().server_version = 'minecraft-pi'
        w.camera.third_person(w.player)
        c().send.assert_called_with('camera.mode.setFollow()')
        w.camera.third_person(w.players[3])
        c().send.assert_called_with('camera.mode.setFollow(3)')
        c().server_version = 'raspberry-juice'
        with pytest.raises(NotSupported):
            w.camera.third_person(w.player)
