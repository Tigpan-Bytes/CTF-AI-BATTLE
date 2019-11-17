import random
import math


class AI:
    def __init__(self, width, height):
        self.hiveCount = 0
        self.width = width
        self.height = height

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

    def do_turn(self, grid, position):
        for _ in range(5):
            while True:
                xy = self.get_rand_xy()
                if grid[(position[0] + xy[0]) % self.width][(position[1] + xy[1]) % self.height].walkable:
                    position = ((position[0] + xy[0]) % self.width, (position[1] + xy[1]) % self.height)
                    break
        return position