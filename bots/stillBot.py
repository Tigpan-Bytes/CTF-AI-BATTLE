import random
import math


class AI:
    def __init__(self, width, height):
        self.hiveCount = 0
        self.state = random.randrange(0, 3)
        self.width = width
        self.height = height

    def get_state_xy(self):
        if self.state == 0:
            return 0, 1
        elif self.state == 1:
            return 1, 0
        elif self.state == 2:
            return 0, -1
        else:
            return -1, 0

    def do_turn(self, grid, width, height, position):
        if grid[(position[0] + 1) % width][position[1]].walkable:
            return position[0] + 1, position[1]
        return position
