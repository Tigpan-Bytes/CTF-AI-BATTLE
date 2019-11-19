import random
import math
from class_data import *


class AI:
    def __init__(self, index, world):
        self.index = index
        self.world = world
        self.attacked_hives = []

    def is_enemy_hive(self, tile, position):
        return tile.hive and tile.hive_index != self.index and tile.hive_index not in self.attacked_hives

    def do_turn(self, bees):
        for bee in bees:
            if random.randint(0, 20) == 0:
                bee.action = 'M ' + random.choice(['N','E','S','W'])
            else:
                path = self.world.breadth_search(bee.position, self.is_enemy_hive)
                if path is not None and len(path.direction) >= 1:
                    bee.action = 'M ' + path.direction[0]
                else:
                    cell = self.world.get_tile(bee.position.x, bee.position.y)
                    if self.is_enemy_hive(cell, bee.position):
                        self.attacked_hives.append(cell.hive_index)
                        if len(self.attacked_hives) >= 6:
                            self.attacked_hives.pop(random.randint(0,5))
        return bees
