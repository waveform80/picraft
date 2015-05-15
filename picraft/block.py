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


import io
from collections import namedtuple
from pkg_resources import resource_stream


def _read_blocks_db(filename_or_object):
    if isinstance(filename_or_object, str):
        stream = io.open(filename_or_object, 'rb')
    else:
        stream = filename_or_object
    for line in stream:
        line = line.decode('utf-8').strip()
        if line and not line.startswith('#'):
            id, data, pi, pocket, name, description = line.split(None, 5)
            yield int(id), int(data), bool(int(pi)), bool(int(pocket)), name, description


_BLOCKS_DB = {
    (id, data): (pi, pocket, name, description)
    for (id, data, pi, pocket, name, description) in
        _read_blocks_db(resource_stream(__name__, 'block.data'))
    }

_BLOCKS_BY_ID = {
    id: (pi, pocket, name)
    for (id, data), (pi, pocket, name, description) in _BLOCKS_DB.items()
    if data == 0
    }

_BLOCKS_BY_NAME = {
    name: id
    for (id, data), (pi, pocket, name, description) in _BLOCKS_DB.items()
    if data == 0
    }


class Block(namedtuple('Block', ('id', 'data'))):
    """
    Represents a block within the Minecraft world.

    Blocks within the Minecraft world are represented by two values: an *id*
    which defines the type of the block (air, stone, grass, wool, etc.) and an
    optional *data* value (defaults to 0) which means different things for
    different block types (e.g.  for wool it defines the color of the wool).

    Blocks are represented by this library as a :func:`namedtuple` of the *id*
    and the *data*. Calculated properties are provided to look up the
    :attr:`name` and :attr:`description` of the block from a database derived
    from the Minecraft wiki, and classmethods are defined to construct a block
    definition from alternate things like a :meth:`name <from_name>` or an
    :meth:`RGB color <from_color>`.

    Aliases are provided for compatibility with the official reference
    implementation (AIR, GRASS, STONE, etc).
    """

    def __new__(cls, id, data=0):
        # This is simply overridden to change data to an optional param
        return super(Block, cls).__new__(cls, id, data)

    @classmethod
    def from_string(cls, s):
        id, data = s.split(',', 1)
        return cls(int(id), int(data))

    @classmethod
    def from_name(cls, name, data=0):
        """
        Construct a :class:`Block` instance from a *name*, as returned by the
        :attr:`name` property. This may be used to construct blocks in a more
        "friendly" way within code. For example::

            >>> from picfraft import *
            >>> g = Game()
            >>> g.blocks[Vector(0,0,0):Vector(5,5,5)] = Block.from_name('stone')
            >>> g.blocks[Vector(1,1,1):Vector(3,3,3)] = Block.from_name('air')

        The optional *data* parameter can be used to specify the data component
        of the new :class:`Block` instance; it defaults to 0.
        """
        try:
            id = _BLOCKS_BY_NAME[name]
        except KeyError:
            raise ValueError('unknown name %s' % name)
        return cls(id, data)

    @classmethod
    def from_color(cls, red, green, blue):
        raise NotImplemented

    def __repr__(self):
        try:
            return '<Block "%s" id=%d data=%d>' % (self.name, self.id, self.data)
        except KeyError:
            return '<Block id=%d data=%d>' % (self.id, self.data)

    @property
    def pi(self):
        """
        Returns a bool indicating whether the block is present in the Pi
        Edition of Minecraft.
        """
        return _BLOCKS_BY_ID[self.id][0]

    @property
    def pocket(self):
        """
        Returns a bool indicating whether the block is present in the Pocket
        Edition of Minecraft.
        """
        return _BLOCKS_BY_ID[self.id][1]

    @property
    def name(self):
        """
        Return the name of the block. This is a unique identifier string which
        can be used to construct a :class:`Block` instance with
        :meth:`from_name`.
        """
        return _BLOCKS_BY_ID[self.id][2]

    @property
    def description(self):
        """
        Return a description of the block. This string is not guaranteed to be
        unique and is only intended for human use.
        """
        try:
            return _BLOCKS_DB[(self.id, self.data)][3]
        except KeyError:
            return _BLOCKS_DB[(self.id, 0)][3]


class Blocks(object):
    """
    This property can be queried to determine the type of a block in the world,
    or can be set to alter the type of a block. The property can be indexed
    with a single :class:`Vector`, in which case the state of a single block is
    returned (or updated) as a :class:`Block` instance::

        >>> game.blocks[g.player.tile_pos]
        <Block "grass" id=2 data=0>

    Alternatively, a slice of two vectors can be used. In this case, when
    querying the property, a sequence of :class:`Block` instances is returned,
    When setting a slice of two vectors you can either pass a sequence of
    :class:`Block` instances or a single :class:`Block` instance. The sequence
    must be equal to the number of blocks represented by the slice::

        >>> game.blocks[Vector(0,0,0):Vector(1,0,0)]
        [<Block "grass" id=2 data=0>,<Block "grass" id=2 data=0>]
        >>> game.blocks[Vector(0,0,0):Vector(5,0,5)] = Block.from_name('grass')

    As with normal Python slices, the interval specified is `half-open`_.  That
    is to say, it is inclusive of the lower vector, *not* the upper one. Hence,
    ``Vector():Vector(x=5)`` represents the coordinates (0,0,0) to (4,0,0).

    .. half-open: http://python-history.blogspot.co.uk/2013/10/why-python-uses-0-based-indexing.html

    .. warning:

        Querying or setting sequences of blocks is extremely slow as a network
        transaction must be executed for each individual block.  When setting a
        slice of blocks, this can be speeded up by specifying a single
        :class:`Block` in which case one network transaction will occur to set
        all blocks in the slice.  Additionally, a :meth:`connection batch
        <picraft.connection.Connection.batch_start>` can be used to speed
        things up.
        """
    def __init__(self, connection):
        self._connection = connection

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise NotImplemented
        else:
            return Block.from_string(
                self._connection.transact(
                    'world.getBlockWithData(%d,%d,%d)' % (index.x, index.y, index.z)))

    def __setitem__(self, index, value):
        pass
        if isinstance(index, slice):
            if hasattr(value, 'id') and hasattr(value, 'data'):
                self._connection.send(
                    'world.setBlocks(%d,%d,%d,%d,%d,%d,%d,%d)' % (
                        index.start.x, index.start.y, index.start.z,
                        index.stop.x - 1, index.stop.y - 1, index.stop.z - 1,
                        value.id, value.data))
            else:
                raise NotImplemented
        else:
            self._connection.send(
                'world.setBlock(%d,%d,%d,%d,%d)' % (
                    index.x, index.y, index.z, value.id, value.data))


AIR                 = Block(0)
STONE               = Block(1)
GRASS               = Block(2)
DIRT                = Block(3)
COBBLESTONE         = Block(4)
WOOD_PLANKS         = Block(5)
SAPLING             = Block(6)
BEDROCK             = Block(7)
WATER_FLOWING       = Block(8)
WATER               = WATER_FLOWING
WATER_STATIONARY    = Block(9)
LAVA_FLOWING        = Block(10)
LAVA                = LAVA_FLOWING
LAVA_STATIONARY     = Block(11)
SAND                = Block(12)
GRAVEL              = Block(13)
GOLD_ORE            = Block(14)
IRON_ORE            = Block(15)
COAL_ORE            = Block(16)
WOOD                = Block(17)
LEAVES              = Block(18)
GLASS               = Block(20)
LAPIS_LAZULI_ORE    = Block(21)
LAPIS_LAZULI_BLOCK  = Block(22)
SANDSTONE           = Block(24)
BED                 = Block(26)
COBWEB              = Block(30)
GRASS_TALL          = Block(31)
WOOL                = Block(35)
FLOWER_YELLOW       = Block(37)
FLOWER_CYAN         = Block(38)
MUSHROOM_BROWN      = Block(39)
MUSHROOM_RED        = Block(40)
GOLD_BLOCK          = Block(41)
IRON_BLOCK          = Block(42)
STONE_SLAB_DOUBLE   = Block(43)
STONE_SLAB          = Block(44)
BRICK_BLOCK         = Block(45)
TNT                 = Block(46)
BOOKSHELF           = Block(47)
MOSS_STONE          = Block(48)
OBSIDIAN            = Block(49)
TORCH               = Block(50)
FIRE                = Block(51)
STAIRS_WOOD         = Block(53)
CHEST               = Block(54)
DIAMOND_ORE         = Block(56)
DIAMOND_BLOCK       = Block(57)
CRAFTING_TABLE      = Block(58)
FARMLAND            = Block(60)
FURNACE_INACTIVE    = Block(61)
FURNACE_ACTIVE      = Block(62)
DOOR_WOOD           = Block(64)
LADDER              = Block(65)
STAIRS_COBBLESTONE  = Block(67)
DOOR_IRON           = Block(71)
REDSTONE_ORE        = Block(73)
SNOW                = Block(78)
ICE                 = Block(79)
SNOW_BLOCK          = Block(80)
CACTUS              = Block(81)
CLAY                = Block(82)
SUGAR_CANE          = Block(83)
FENCE               = Block(85)
GLOWSTONE_BLOCK     = Block(89)
BEDROCK_INVISIBLE   = Block(95)
STONE_BRICK         = Block(98)
GLASS_PANE          = Block(102)
MELON               = Block(103)
FENCE_GATE          = Block(107)
GLOWING_OBSIDIAN    = Block(246)
NETHER_REACTOR_CORE = Block(247)

