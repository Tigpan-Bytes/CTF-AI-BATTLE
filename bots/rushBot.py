# Rusher Bot
# Written by Chad McCool
# Member of team: h4x0rz

# THESE ARE ALL THE IMPORTS ALLOWED, IMPORTING MORE WILL GET YOUR BOT REMOVED ***DO NOT TOUCH THESE***
import random
import math
import itertools
from class_data import *
# THESE ARE ALL THE IMPORTS ALLOWED, IMPORTING MORE WILL GET YOUR BOT REMOVED ***DO NOT TOUCH THESE***
# You also by extension get all the imports in class_data

# BEHAVIOR:
# Find the closest enemy hive using a breadth first search.
# Store the path to that tile in the bee.data
# Move on that path and remove the first direction in the bee.data string

# KNOWN PROBLEMS:
# 1. If you bump into something, your path is then skewed and you will not reach the correct destination anymore.
# 2. This bot doesn't make an attempt to attack enemy bees, collect food, or run away from bees.
# 3. There is no need to use breadth_search when you know the positions of all the hives and that they will be relatively constant.
#       You could use breadth_path to store a path dictionary, then access the path at the bees location to find the direction
#       to get to the nearest hive. You could create the path by calling breadth_path with a list of all hives.
#       I think there is a way to get hive_positions from the enemies in the do_turn function (I can't remember, read the documentation).
#       Then access that path by using path[bee.position]. This would be much MUCH   M U C H   faster than breadth_search if you only
#       recalculate path when a hive is destroyed.
# 4. Overall it is a very bad bot, although it has a chance to get some early points and maybe take a 3rd place podium if every one else is bad.

class AI:
    def __init__(self, index):
        """Initializes the AI with its index and world.
            If you want to store data that is used from turn to turn, put it here."""
        self.index = index
        self.world = None # world is supplied slightly later by the main game

    def is_enemy_hive(self, position, distance):
        """A function passed into self.world.breadth_search to determine if the cell is the end.
            This function just looks for if the tile contains an enemy cell"""
        tile = self.world.get_tile(position.x, position.y)
        return tile.hive and tile.hive_index != self.index

    def update_tiles(self, food_changes, bee_changes, lost_hive_changes):
        """It is not recommended to change this function unless you are ABSOLUTELY sure you know what you are doing.
            This is called once before asking for actions with all the data from the previous round. Then again if a bot was terminated
            containing only the data for the terminated bots (bots that had a runtime error)."""
        for change in food_changes:
            self.world.get_tile(change[1], change[2]).food = change[0]
        for change in bee_changes:
            # It is not recommended to use the bee_changes list to do or store anything, as it may have many overlapping entries
            self.world.get_tile(change[1], change[2]).bee = change[0]
        for change in lost_hive_changes:
            self.world.get_tile(change.x, change.y).hive = False
            self.world.get_tile(change.x, change.y).hive_index = -1

    def do_turn(self, bees, enemies, turn):
        """For simple bots this is the only function that is needed to be changed.
            This function takes in the parameters:
             'bees' which is the list of all the players bees.
             'enemies' which is a list of enemies in which each entry is a list containing data about the enemy:
                each entry contains [the index of the enemy, a list of the positions of their hives, the amount of bees they have]
             'turn' what is the turn number
            This should change bee.action and bee.data, then return them."""

        for bee in bees:
            # loops through every single bee
            if bee.data == '':
                # if the bee currently has no data (.data is a string held by every bee that is kept through turns)
                # use .data to optimize your code and to give memory to the bees
                
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

        return [(bee.data, bee.action) for bee in bees]