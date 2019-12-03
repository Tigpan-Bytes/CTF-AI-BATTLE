# Defend or Wander bot
# Written by Hacker-man Mann
# Member of team: m0r3_1337

# THESE ARE ALL THE IMPORTS ALLOWED, IMPORTING MORE WILL GET YOUR BOT REMOVED ***DO NOT TOUCH THESE***
import random
import math
import itertools
from class_data import *
# THESE ARE ALL THE IMPORTS ALLOWED, IMPORTING MORE WILL GET YOUR BOT REMOVED ***DO NOT TOUCH THESE***
# You also by extension get all the imports in class_data

# BEHAVIOR:
# When a bee has no data (just created bee) assign it randomly D or W
# If the bee is D, then make it stay in place and attack any enemy bees that get close to it
# If the bee is W, then make it move randomly.

# KNOWN PROBLEMS:
# 1. The W bees don't really do anything other than serve as a distraction to enemies invading.
# 2. This bot doesn't make an attempt to attack enemy hives, collect food, or run away from bad fights.
# 3. Using a breadth_search to find attackable bees is slow and has the problem of not allowing you to shoot through walls.
#       using get_x_in_range with a range of 3, would be much faster and allow you to shoot through walls. It also has the added
#       benefit of allowing you to sort through all the targets found (so you could finish off low health bees quicker).
# 4. Overall it is a kinda bad bot, although it has a good chance of lasting a little while because it doesn't attract attention.

class AI:
    def __init__(self, index):
        """Initializes the AI with its index and world.
            If you want to store data that is used from turn to turn, put it here."""
        self.index = index
        self.world = None # world is supplied slightly later by the main game

    def defend_area(self, position, distance):
        """A function passed into self.world.breadth_search to determine if the cell is the end.
            This function just looks for if the tile contains an enemy bee"""
        tile = self.world.get_tile(position.x, position.y)
        return tile.bee is not None and tile.bee.index != self.index

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
                
                bee.data = random.choice(['D', 'W'])
                # randomly assign the bees data to be either D (defend) or W (wander)

            if bee.data == 'D':
                attackable = self.world.breadth_search(bee.position, self.defend_area, 3)
                # breadth_search returns a MovePosition position class, with .x and .y of the final position
                # and .direction of the path needed to reach that position

                # in this case it search the area that is a maximum of 3 tiles away (the bees attacking range), for any enemy bees

                if attackable is not None:
                    # if an enemy bee was found
                    bee.action = 'A ' + str(attackable.x) + ',' + str(attackable.y)
                    # then attack that enemy bee
            else:
                # If the bees state is set to wander then move randomly around
                bee.action = 'M ' + random.choice(['N','E','S','W'])

        return [(bee.data, bee.action) for bee in bees]