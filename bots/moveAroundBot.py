import random
import math

class AI:
    def __init__(self):
        self.hiveCount = 0
        self.state = 0
        
    def do_turn(self, position):
        if self.state == 0:
            returnable = position[0], position[1] + 1
            if returnable[1] == 29:
                self.state = 1
            return returnable
        if self.state == 1:
            returnable = position[0] + 1, position[1]
            if returnable[0] == 29:
                self.state = 2
            return returnable
        if self.state == 2:
            returnable = position[0], position[1] - 1
            if returnable[1] == 0:
                self.state = 3
            return returnable
        if self.state == 3:
            returnable = position[0] - 1, position[1]
            if returnable[0] == 0:
                self.state = 0
            return returnable