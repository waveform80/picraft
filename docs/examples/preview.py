from picraft import World, Model, Block

m = Model('shuttle.obj').render(materials=lambda face: Block('stone'))

with World() as w:
    with w.connection.batch_start():
        for v, b in m.items():
            w.blocks[v + 20*Y] = b
