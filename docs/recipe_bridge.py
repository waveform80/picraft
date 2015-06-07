#!/usr/bin/env python

from __future__ import unicode_literals

import time
from picraft import World, Vector, Block
from collections import deque

world = World(ignore_errors=True)
world.say('Auto-bridge active')
try:
    bridge = deque()
    last_pos = None
    while True:
        this_pos = world.player.pos
        if last_pos is not None:
            # Has the player moved more than 0.1 units in a horizontal direction?
            movement = (this_pos - last_pos).replace(y=0.0)
            if movement.magnitude > 0.1:
                # Find the next tile they're going to step on
                next_pos = (this_pos + movement.unit).floor() - Vector(y=1)
                if world.blocks[next_pos] == Block('air'):
                    with world.connection.batch_start():
                        bridge.append(next_pos)
                        world.blocks[next_pos] = Block('diamond_block')
                        while len(bridge) > 10:
                            world.blocks[bridge.popleft()] = Block('air')
        last_pos = this_pos
        time.sleep(0.01)
except KeyboardInterrupt:
    world.say('Auto-bridge deactivated')
    with world.connection.batch_start():
        while bridge:
            world.blocks[bridge.popleft()] = Block('air')

