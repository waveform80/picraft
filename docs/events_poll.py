from time import sleep
from picraft import World

world = World()

while True:
    for event in world.events.poll():
        world.say('Player %d hit face %s of block at %d,%d,%d' % (
            event.player.player_id, event.face,
            event.pos.x, event.pos.y, event.pos.z))
    sleep(0.1)

