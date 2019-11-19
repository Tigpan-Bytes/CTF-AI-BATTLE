import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.index = index

    def is_enemy_hive(self, tile, position):
        return tile.hive and tile.hive_index != self.index

    def do_turn(self, world, bees):
        for bee in bees:
            path = world.breadth_search(bee.position, self.is_enemy_hive)
            if path is not None and len(path.direction) >= 1:
                bee.action = 'M ' + path.direction[0]
        return bees
