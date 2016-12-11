from random import randint
from time import sleep
from picraft import World, X, Y, Z, Vector, Block

world = World()

p = world.player.tile_pos
white_pos = p - 2 * X
black_pos = p - 3 * X

world.blocks[white_pos] = Block('#ffffff')
world.blocks[black_pos] = Block('#000000')

running = True
while running:
    for event in world.events.poll():
        if event.pos == white_pos:
            rain = Vector(p.x + randint(-10, 10), p.y + 20, p.z + randint(-10, 10))
            rain_end = world.height[rain]
            world.blocks[rain] = Block('wool', randint(1, 15))
            while rain != rain_end:
                with world.connection.batch_start():
                    world.blocks[rain] = Block('air')
                    rain -= Y
                    world.blocks[rain] = Block('wool', randint(1, 15))
                    sleep(0.1)
        elif event.pos == black_pos:
            running = False
