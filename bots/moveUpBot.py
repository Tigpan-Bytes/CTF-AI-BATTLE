import random
import math

class AI:
    def __init__(self):
        self.hiveCount = 0
        
    def do_turn(position):
        return (position[0], (position[1] + 1) % 30)