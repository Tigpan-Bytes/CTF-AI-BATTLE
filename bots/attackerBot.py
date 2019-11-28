import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.world = None
        self.index = index
        self.attacked_hives = [index]

    def is_enemy_hive(self, position):
        tile = self.world.get_tile(position.x, position.y)
        return tile.hive_index not in self.attacked_hives

    def update_tiles(self, food_changes, bee_changes):
        """It is not recommended to change this function unless you are ABSOLUTELY sure you know what you are doing"""
        for change in food_changes:
            self.world.get_tile(change[1], change[2]).food = change[0]
        for change in bee_changes:
            self.world.get_tile(change[1], change[2]).bee = change[0]

    def do_turn(self, bees):
        for bee in bees:
            if random.randint(0, 10) == 0:
                bee.action = 'M ' + random.choice(['N','E','S','W'])
            else:
                path = self.world.breadth_search(bee.position, self.is_enemy_hive)
                if path is not None and len(path.direction) >= 1:
                    bee.action = 'M ' + path.direction[0]
                else:
                    cell = self.world.get_tile(bee.position.x, bee.position.y)
                    if self.is_enemy_hive(bee.position):
                        self.attacked_hives.append(cell.hive_index)
                        if len(self.attacked_hives) >= 8:
                            self.attacked_hives.pop(random.randint(1,7))
        return [(bee.data, bee.action) for bee in bees]
