import random
import math
from class_data import *


class AI:
    def __init__(self, index, world):
        self.index = index
        self.world = world

    def do_turn(self, bees):
        self.world.tiles.reverse()
        for bee in bees:
            bee.position = bee.position.x + 1, bee.position.y + 1
            bee.action = "M N"
        return bees
