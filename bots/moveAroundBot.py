import random
import math


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
    def __init__(self, width, height):
        self.hiveCount = 0
        self.width = width
        self.height = height

    def do_turn(self, grid, bees):
        for bee in bees:
            if bee.data == '':
                bee.data = '0'
            while True:
                xya = get_state_xy(bee.data)
                if grid[(bee.position[0] + xya[0]) % self.width][(bee.position[1] + xya[1]) % self.height].walkable:
                    bee.action = 'M ' + xya[2]
                    break
                bee.data = str((int(bee.data) + 1) % 4)
        return bees
