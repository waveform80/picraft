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


def track_changes(states, default=Block('air')):
    old_state = None
    for state in states:
        if old_state is None:
            old_state = {v: default for v in state}
        changes = {v: b for v, b in state.items() if old_state.get(v) != b}
        changes.update({v: default for v in old_state if v not in state})
        yield changes
        old_state = state


world = World()
world.checkpoint.save()
try:
    for state in track_changes(animation_frames(20)):
        with world.connection.batch_start():
            for v, b in state.items():
                world.blocks[v] = b
        sleep(0.2)
finally:
    world.checkpoint.restore()
