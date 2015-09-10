from picraft import Model, World, X, Y, Z

with World() as w:
    p = w.player.tile_pos - 3*X + 5*Z
    with w.connection.batch_start():
        for v, b in Model('house.obj').render().items():
            w.blocks[v + p] = b
