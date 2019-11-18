import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.index = index

    def do_turn(self, world, bees):
        world.tiles = world.tiles.reverse()
        for bee in bees:
            bee.position = bee.position.x + 1, bee.position.y + 1
            bee.action = "M N"
        return bees