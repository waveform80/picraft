from __future__ import division

import math
from picraft import World, Vector, O, X, Y, Z, lines

def polygon(sides, center=O, radius=5):
    angle = 2 * math.pi / sides
    for side in range(sides):
        yield Vector(
                center.x + radius * math.cos(side * angle),
                center.y + radius * math.sin(side * angle))

def shapes():
    for sides in range(3, 9):
        yield lines(polygon(sides, center=3*Y))

w = World()
for shape in shapes():
    # Draw the shape
    with w.connection.batch_start():
        for p in shape:
            w.blocks[p] = Block('stone')
    sleep(0.5)
    # Wipe the shape
    with w.connection.batch_start():
        for p in shape:
            w.blocks[p] = Block('air')
