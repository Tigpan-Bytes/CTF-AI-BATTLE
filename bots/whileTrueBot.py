import random
import math
from class_data import *

class AI:
    def __init__(self, index):
        self.world = None
        self.index = index

    def do_turn(self, bees):
        i = 0
        for bee in bees:
            if random.randint(0, 20) == 0:
                bee.action = 'M ' + random.choice(['N','S','E','W'])
        return [(bee.data, bee.action) for bee in bees]
