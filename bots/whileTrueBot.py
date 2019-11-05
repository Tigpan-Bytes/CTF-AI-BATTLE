import random
import math

class AI:
    def __init__(self, width, height):
        self.hiveCount = 0
        self.width = width
        self.height = height
        
    def do_turn(self, position):
        i = 0
        while True:
            i = (i + 1) % 1000
        return (position[0]+1, position[1]+1)