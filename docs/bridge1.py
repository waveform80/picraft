from __future__ import unicode_literals

import time
from picraft import World, Vector, Block, Y

world = World()
last_pos = None
while True:
    this_pos = world.player.pos
    if last_pos is not None:
        # Has the player moved more than 0.1 units in a horizontal direction?
        movement = (this_pos - last_pos).replace(y=0.0)
        if movement.magnitude > 0.1:
            # Find the next tile they're going to step on
            next_pos = (this_pos + movement.unit).floor() - Y
            world.blocks[next_pos] = Block('diamond_block')
    last_pos = this_pos
    time.sleep(0.01)

