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
        i = 0
        for bee in bees:
            if random.randint(0, 20) == 0:
                bee.action = 'M ' + random.choice(['N','S','E','W'])
        return [(bee.data, bee.action) for bee in bees]
