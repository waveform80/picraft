from __future__ import division

import math
from time import sleep
from picraft import World, Vector, Block, O, X, Y, Z, lines

def polygon(sides, center=O, radius=5):
    angle = 2 * math.pi / sides
    for side in range(sides):
        yield Vector(
                center.x + radius * math.cos(side * angle),
                center.y + radius * math.sin(side * angle),
                center.z).round()

def shapes(center=O):
    for sides in range(3, 9):
        yield lines(polygon(sides, center=center))

w = World()
for shape in shapes(w.player.tile_pos + 15*Y + 10*Z):
    # Copy the generator into a list so we can re-use
    # the coordinates
    shape = list(shape)
    # Draw the shape
    with w.connection.batch_start():
        for p in shape:
            w.blocks[p] = Block('gold_block')
    sleep(0.5)
    # Wipe the shape
    with w.connection.batch_start():
        for p in shape:
            w.blocks[p] = Block('air')
