from __future__ import division

import math
from picraft import World, Vector, O, X, Y, Z, lines

def polygon(sides, center=O, radius=5):
    angle = 2 * math.pi / sides
    for side in range(sides):
        yield Vector(
                center.x + radius * math.cos(side * angle),
                center.y + radius * math.sin(side * angle))

print(list(polygon(3, center=3*Y)))
print(list(polygon(4, center=3*Y)))
print(list(polygon(5, center=3*Y)))

