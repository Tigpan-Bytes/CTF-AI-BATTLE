import random
import math
from class_data import *


def get_state_xy(state):
    if state == '0':
        return 0, 1, 'N'
    elif state == '1':
        return 1, 0, 'E'
    elif state == '2':
        return 0, -1, 'S'
    else:
        return -1, 0, 'W'


class AI:
    def __init__(self):
        self.hiveCount = 0

    def do_turn(self, world, bees):
        for bee in bees:
            if bee.data == '':
                bee.data = str(random.randint(0,3))
            while True:
                xya = get_state_xy(bee.data)
                if world.get_tile(bee.position.x + xya[0], bee.position.y + xya[1]).walkable:
                    bee.action = 'M ' + xya[2]
                    break
                bee.data = str((int(bee.data) + 1) % 4)
        return bees
