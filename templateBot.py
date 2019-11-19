# These are all the imports that are allowed in your bot. Importing more will get your bot removed
import random
import math
from class_data import *
# These are all the imports that are allowed in your bot. Importing more will get your bot removed


class AI:
    def __init__(self, index, world):
        """Initilizes the AI with its index and world"""
        self.index = index
        self.world = world

    def is_enemy_hive(self, tile, position):
        """A function passed into self.world.breadth_search to determine if the cell is the end.
            This function just looks for if the tile contains an enemy cell"""
        return tile.hive and tile.hive_index != self.index

    def do_turn(self, bees):
        """For simple bots this is the only function that is needed to be changed.
            This function takes in a paramter 'bees' which is the list of all the players bees.
            Changes bee.action and bee.data, then returns."""
        for bee in bees:
            #loops through every single bee
            if bee.data == '':
                # if the bee currently has no data (.data is a string held by every bee that is kept through turns)
                # use .data to optimize your code and to give memory to the
                
                movement = self.world.breadth_search(bee.position, self.is_enemy_hive)
                # breadth_search returns a MovePosition position class, with .x and .y of the final position
                # and .direction of the path needed to reach that position
                
                if movement is not None: # breadth_search will return None if no path can be found
                    bee.data = movement.direction
                    # sets the bees .data string to the path needed to reach the end
            if len(bee.data) >= 1:
                # only move if the path length is greater than one (this will only not check if you are currently at the end
                
                bee.action = 'M ' + bee.data[0]
                # sets the bee.action to 'M N' (the N (north) can be either N, E, S, or W)
                # action is a string that is cleared after each turn it can either with 'M ' or 'A ' M means move, and A means attack
                bee.data = bee.data[1:]
                # takes the first direction off of the bees path
        return bees