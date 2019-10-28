import random
import math

class AI:
    def __init__(self):
        self.hiveCount = 0
        
    def do_turn(position):
        return (random.randrange(0, 30), random.randrange(0, 30))