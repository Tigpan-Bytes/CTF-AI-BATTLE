import random
import math

class AI:
    def __init__(self, width, height):
        self.hiveCount = 0
        self.width = width
        self.height = height
        
    def do_turn(self, position):
        return (position[0] + random.randrange(-1, 2) + self.width) % self.width, (position[1] + random.randrange(-1, 2) + self.height) % self.height