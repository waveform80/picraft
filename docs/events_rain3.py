from random import randint
from picraft import World, X, Y, Z, Vector, Block

world = World()

p = world.player.tile_pos
white_pos = p - 2 * X
black_pos = p - 3 * X

world.blocks[white_pos] = Block('#ffffff')
world.blocks[black_pos] = Block('#000000')

@world.events.block_hit(pos=black_pos)
def stop_script(event):
    world.connection.close()

@world.events.block_hit(pos=white_pos, thread=True)
def make_it_rain(event):
    rain = Vector(p.x + randint(-10, 10), p.y + 20, p.z + randint(-10, 10))
    rain_end = world.height[rain]
    world.blocks[rain] = Block('wool', randint(1, 15))
    while rain != rain_end:
        with world.connection.batch_start():
            world.blocks[rain] = Block('air')
            rain -= Y
            world.blocks[rain] = Block('wool', randint(1, 15))

world.events.main_loop()

