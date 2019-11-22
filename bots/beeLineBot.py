import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.index = index

    def do_turn(self, world, bees):
        for bee in bees:
            if bee.data == '':
                bee.data = world.depth_search(bee.position, Position(32 * random.randint(0, 2), 32 * random.randint(0, 2))).direction
            if bee.data != '':
                bee.action = 'M ' + bee.data[0]
                bee.data = bee.data[1:]
        return bees
