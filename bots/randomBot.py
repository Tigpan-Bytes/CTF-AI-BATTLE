import random
import math


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
    def __init__(self, width, height):
        self.hiveCount = 0
        self.width = width
        self.height = height

    def do_turn(self, grid, bees):
        for bee in bees:
            while True:
                xya = get_rand_xy()
                if grid[(bee.position[0] + xya[0]) % self.width][(bee.position[1] + xya[1]) % self.height].walkable:
                    bee.action = 'M ' + xya[2]
                    break
        return bees
