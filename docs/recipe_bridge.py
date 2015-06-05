#!/usr/bin/env python

import time
from picraft import World, Vector, Block

world = World(ignore_errors=True)
world.say('Auto-bridge active')

last_pos = None
while True:
    this_pos = world.player.pos
    if last_pos is not None:
        # Has the player moved more than 0.2 units in a horizontal direction?
        movement = (this_pos - last_pos).replace(y=0.0)
        if movement.magnitude > 0.1:
            # Find the next tile they're going to step on
            next_pos = (this_pos + movement.unit).floor() - Vector(y=1)
            if world.blocks[next_pos] == Block('air'):
                world.blocks[next_pos] = Block('diamond_block')
    last_pos = this_pos
    time.sleep(0.01)

