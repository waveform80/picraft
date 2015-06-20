from __future__ import division

from time import sleep
from picraft import *


def animation_frames(count):
    cube_range = vector_range(Vector() - 2, Vector() + 2 + 1)
    for frame in range(count):
        state = {}
        for v in cube_range:
            state[v.rotate(15 * frame, about=X).round() + (5 * Y)] = Block('stone')
        yield state


world = World()
world.checkpoint.save()
try:
    for frame in animation_frames(10):
        # Draw frame
        with world.connection.batch_start():
            for v, b in frame.items():
                world.blocks[v] = b
        sleep(0.2)
        # Wipe frame
        with world.connection.batch_start():
            for v, b in frame.items():
                world.blocks[v] = Block('air')
finally:
    world.checkpoint.restore()
