import random
import math

class AI:
    def __init__(self):
        self.hiveCount = 0
        
    def do_turn(self, position):
        return (position[0] + random.randrange(-1, 2) + 30) % 30, (position[1] + random.randrange(-1, 2) + 30) % 30