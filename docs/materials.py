from picraft import World, Model, Block

print('Loading model airboat.obj')
m = Model('airboat.obj')
print('Model has the following materials:')
print('\n'.join(m.materials))

materials_map = {
    None:       Block('stone'),
    'bluteal':  Block('diamond_block'),
    'bronze':   Block('gold_block'),
    'dkdkgrey': Block('#404040'),
    'dkteal':   Block('#000080'),
    'red':      Block('#ff0000'),
    'silver':   Block('#ffffff'),
    'black':    Block('#000000'),
    }

with World() as w:
    with w.connection.batch_start():
        for v, b in m.render(materials=materials_map).items():
            w.blocks[v] = b

