import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.index = index

    def do_turn(self, world, bees):
        for bee in bees:
            if bee.data == '':
                thing = None
                while thing == None:
                    thing = world.depth_search(bee.position, Position(random.randint(0, world.width - 1), random.randint(0, world.width - 1)))
                bee.data = thing.direction
            if bee.data != '' and len(bee.data) >= 1:
                bee.action = 'M ' + bee.data[0]
                bee.data = bee.data[1:]
        return bees
