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
import warnings
import io
import picraft.block
from picraft import Block, Vector, vector_range, EmptySliceWarning
try:
    from unittest import mock
except ImportError:
    import mock


def test_read_block_data_filename():
    with mock.patch('io.open'):
        io.open.return_value = [b'1 0 1 1 test Test']
        assert list(picraft.block._read_block_data('foo.txt')) == [(1, 0, True, True, 'test', 'Test')]

def test_read_block_data_file_obj():
    data = [b'1 0 1 1 test Test']
    assert list(picraft.block._read_block_data(data)) == [(1, 0, True, True, 'test', 'Test')]

def test_read_block_color_filename():
    with mock.patch('io.open'):
        io.open.return_value = [b'1 0 ffffff', b'1 1 000000']
        assert list(picraft.block._read_block_color('foo.txt')) == [(1, 0, (255, 255, 255)), (1, 1, (0, 0, 0))]

def test_block_init():
    assert Block(1, 1) == Block.from_id(1, 1)
    assert Block(b'stone') == Block.from_name('stone')
    assert Block('stone') == Block.from_name('stone')
    assert Block('air', 1) == Block.from_name('air', 1)
    assert Block('#ffffff') == Block.from_color('#ffffff')
    assert Block((0, 0, 0)) == Block.from_color((0, 0, 0))
    assert Block(id=1) == Block.from_id(1)
    assert Block(name='grass') == Block.from_name('grass')
    assert Block(color='#ffffff', exact=False) == Block.from_color('#ffffff')
    with pytest.raises(TypeError):
        Block()
    with pytest.raises(TypeError):
        Block(1, 2, 3)

def test_block_from_string():
    assert Block.from_string('1,1') == Block(1, 1)
    with pytest.raises(ValueError):
        Block.from_string('foo')
    with pytest.raises(ValueError):
        Block.from_string('1.0,2.0')

def test_block_from_name():
    assert Block.from_name(b'air') == Block(0, 0)
    assert Block.from_name('air') == Block(0, 0)
    assert Block.from_name('stone') == Block(1, 0)
    with pytest.raises(ValueError):
        Block.from_name('foobarbaz')

def test_block_from_color():
    assert Block.from_color(b'#ffffff') == Block(35, 0)
    assert Block.from_color('#ffffff') == Block(35, 0)
    assert Block.from_color((255, 255, 255)) == Block(35, 0)
    assert Block.from_color((0.0, 0.0, 0.0)) == Block(35, 15)
    with pytest.raises(ValueError):
        Block.from_color('white')
    with pytest.raises(ValueError):
        Block.from_color((1, 2))

def test_block_from_color_exact():
    with pytest.raises(ValueError):
        Block.from_color(b'#ffffff', exact=True)

def test_block_platforms():
    assert Block.from_name('air').pi
    assert Block.from_name('air').pocket
    assert not Block.from_name('piston').pi
    assert not Block.from_name('piston').pocket

def test_block_name():
    assert Block(0, 0).name == 'air'

def test_block_desc():
    assert Block(35, 15).description == 'Black Wool'
    assert Block(35, 30).description == 'White Wool'

def test_blocks_get_one():
    conn = mock.MagicMock()
    conn.transact.return_value = '1,1'
    assert picraft.block.Blocks(conn)[Vector(1, 2, 3)] == Block(1, 1)
    conn.transact.assert_called_once_with('world.getBlockWithData(1,2,3)')

def test_blocks_get_many():
    v_from = Vector(1, 2, 3)
    v_to = Vector(2, 3, 5)
    conn = mock.MagicMock()
    conn.transact.return_value = '1,1'
    assert picraft.block.Blocks(conn)[v_from:v_to] == [
            Block(1, 1) for v in vector_range(v_from, v_to)]
    for v in vector_range(v_from, v_to):
        conn.transact.assert_any_call(
                'world.getBlockWithData(%d,%d,%d)' % (v.x, v.y, v.z))

def test_blocks_get_many_fast():
    v_from = Vector(1, 2, 3)
    v_to = Vector(2, 3, 5)
    conn = mock.MagicMock()
    conn.server_version = 'raspberry-juice'
    conn.transact.return_value = '1,1'
    picraft.block.Blocks(conn)[v_from:v_to] == [
            Block(1, 0) for v in vector_range(v_from, v_to)]
    conn.transact.assert_called_once_with(
            'world.getBlocks(%s,%s)' % (v_from, v_to - 1))

def test_blocks_get_none():
    conn = mock.MagicMock()
    v_from = Vector(1, 2, 3)
    v_to = Vector(2, 3, 5)
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with pytest.raises(EmptySliceWarning):
            picraft.block.Blocks(conn)[v_to:v_from]

def test_blocks_set_none():
    conn = mock.MagicMock()
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with pytest.raises(EmptySliceWarning):
            picraft.block.Blocks(conn)[Vector(1, 1, 1):Vector(3, 3, -1)] = Block(0, 0)

def test_blocks_set_one():
    conn = mock.MagicMock()
    picraft.block.Blocks(conn)[Vector(1, 2, 3)] = Block(0, 0)
    conn.send.assert_called_once_with('world.setBlock(1,2,3,0,0)')

def test_blocks_set_many_same():
    conn = mock.MagicMock()
    v_from = Vector(1, 2, 3)
    v_to = Vector(2, 3, 5)
    picraft.block.Blocks(conn)[v_from:v_to] = Block(0, 0)
    conn.send.assert_called_once_with('world.setBlocks(1,2,3,1,2,4,0,0)')

def test_blocks_set_many_different():
    conn = mock.MagicMock()
    v_from = Vector(1, 2, 3)
    v_to = Vector(2, 3, 5)
    blocks = [Block(1, 1) for v in vector_range(v_from, v_to)]
    picraft.block.Blocks(conn)[v_from:v_to] = blocks
    for v in vector_range(v_from, v_to):
        conn.send.assert_any_call(
                'world.setBlock(%d,%d,%d,1,1)' % (v.x, v.y, v.z))
    with pytest.raises(ValueError):
        picraft.block.Blocks(conn)[v_from:v_to] = blocks[1:]
    with pytest.raises(ValueError):
        picraft.block.Blocks(conn)[v_from:v_to] = blocks * 2
