from picraft import Model, World

with World() as w:
    with w.connection.batch_start():
        for v, b in Model('house.obj').render().items():
            w.blocks[v] = b
