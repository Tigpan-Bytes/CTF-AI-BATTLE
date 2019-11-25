import random
import math
from class_data import *

class AI:
    def __init__(self, index):
        self.index = index

    def do_turn(self, world, bees):
        world.tiles[random.randint(0, 15)][random.randint(0, 15)].walled = True
        for bee in bees:
            bee.position = Position(bee.position.x + 1, bee.position.y + 1)
            bee.action = "M N"
        return bees
