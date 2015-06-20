from __future__ import division

from time import sleep
from picraft import World, Vector, X, Y, Z, vector_range, Block

world = World()
world.checkpoint.save()
try:
    cube_range = vector_range(Vector() - 2, Vector() + 2 + 1)
    # Draw frame 1
    state = {}
    for v in cube_range:
        state[v + (5 * Y)] = Block('stone')
    with world.connection.batch_start():
        for v, b in state.items():
            world.blocks[v] = b
    sleep(0.2)
    # Wipe frame 1
    with world.connection.batch_start():
        for v in state:
            world.blocks[v] = Block('air')
    # Draw frame 2
    state = {}
    for v in cube_range:
        state[v.rotate(15, about=X).round() + (5 * Y)] = Block('stone')
    with world.connection.batch_start():
        for v, b in state.items():
            world.blocks[v] = b
    sleep(0.2)
    # and so on...
finally:
    world.checkpoint.restore()
