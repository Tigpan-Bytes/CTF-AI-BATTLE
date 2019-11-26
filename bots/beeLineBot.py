import random
import math
from class_data import *


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
            if bee.data == '':
                bee.data = self.world.depth_search(bee.position, Position(32 * random.randint(0, 2), 32 * random.randint(0, 2))).direction
            if bee.data != '':
                bee.action = 'M ' + bee.data[0]
                bee.data = bee.data[1:]
        return [(bee.data, bee.action) for bee in bees]
