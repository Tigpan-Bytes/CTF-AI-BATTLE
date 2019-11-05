import random
import math

class AI:
    def __init__(self, width, height):
        self.hiveCount = 0
        self.state = random.randrange(0, 5)
        self.width = width
        self.height = height
        
    def do_turn(self, position):
        if self.state == 0:
            returnable = position[0], position[1] + 1
            if returnable[1] == self.height - 1:
                self.state = 1
            return returnable
        elif self.state == 1:
            returnable = position[0] + 1, position[1]
            if returnable[0] == self.width - 1:
                self.state = 2
            return returnable
        elif self.state == 2:
            returnable = position[0], position[1] - 1
            if returnable[1] == 0:
                self.state = 3
            return returnable
        else:
            returnable = position[0] - 1, position[1]
            if returnable[0] == 0:
                self.state = 0
            return returnable