import random
import math
from class_data import *


def get_rand_xy():
    val = random.randint(0, 3)
    if val == 0:
        return 0, 1, 'N'
    elif val == 1:
        return 1, 0, 'E'
    elif val == 2:
        return 0, -1, 'S'
    else:
        return -1, 0, 'W'


class AI:
    def __init__(self, index):
        self.index = index

    def do_turn(self, world, bees):
        for bee in bees:
            while True:
                xya = get_rand_xy()
                if world.get_tile(bee.position.x + xya[0], bee.position.y + xya[1]).walkable:
                    bee.action = 'M ' + xya[2]
                    break
        return bees
