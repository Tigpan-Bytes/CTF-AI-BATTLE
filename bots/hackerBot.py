import random
import math
from class_data import *

class AI:
    def __init__(self, index):
        self.world = None
        self.index = index

    def do_turn(self, bees):
        self.world.tiles[random.randint(0, 15)][random.randint(0, 15)] = None
        for bee in bees:
            bee.position = Position(bee.position.x + 1, bee.position.y + 1)
            bee.action = "M N"
        return [(bee.data, bee.action) for bee in bees]
