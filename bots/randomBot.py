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
        self.world = None
        self.index = index

    def update_tiles(self, food_changes, bee_changes):
        """It is not recommended to change this function unless you are ABSOLUTELY sure you know what you are doing"""
        for change in food_changes:
            self.world.get_tile(change[1], change[2]).food = change[0]
        for change in bee_changes:
            self.world.get_tile(change[1], change[2]).bee = change[0]

    def do_turn(self, bees):
        for bee in bees:
            while True:
                xya = get_rand_xy()
                if self.world.get_tile(bee.position.x + xya[0], bee.position.y + xya[1]).walkable:
                    bee.action = 'M ' + xya[2]
                    break
        return [(bee.data, bee.action) for bee in bees]
