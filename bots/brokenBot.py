import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.index = index

    def get_rand_xy(self):
        val = random.randint(0, 3)
        if val == 0:
            return 0, 1
        elif val == 1:
            return 1, 0
        elif val == 2:
            return 0, -1
        else:
            return -1, 0

    def do_turn(self, world, position,e,k,l,u,t,f,xc,fd,ew):
        for _ in range(5):
            while True:
                xy = self.get_rand_xy()
                if world.get_tile(position[0] + xy[0], position[1] + xy[1]).walkable:
                    position = ((position[0] + xy[0]) % self.width, (position[1] + xy[1]) % self.height)
                    break
        return position