from __future__ import division

from time import sleep
from picraft import *


def animation_frames(count):
    cube_range = vector_range(
        Vector() - 2, Vector() + 2 + 1)
    for frame in range(count):
        yield {
            v.rotate(15 * frame, about=X).round() + (5 * Y): Block('stone')
            for v in cube_range}

def minimal_update(new_state, old_state=None, default=Block('air')):
    if old_state is None:
        old_state = {v: default for v in new_state}
    changes = {}
    for v, b in new_state.items():
        if v in old_state and old_state[v] == b:
            continue
        changes[v] = b
    for v, b in old_state.items():
        if not v in new_state:
            changes[v] = default
    return changes, new_state


world = World()
world.checkpoint.save()
try:
    state = None
    for frame in animation_frames(20):
        changes, state = minimal_update(frame, state)
        with world.connection.batch_start():
            for v, b in changes.items():
                world.blocks[v] = b
        sleep(0.2)
finally:
    world.checkpoint.restore()
