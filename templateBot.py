# BOT NAME
# Written by PERSON NAMES
# Member of team: TEAM NAME

import random
import math
from class_data import *

# BEHAVIOR:
# Its a good idea to write out the behavior of the bot here so it is easy for your team to look at and know
# what you wanted to do.

# KNOWN PROBLEMS:
# This should function like a TODO list for you. If you know your bot has problems or ways to be improved, then put them here.

class AI:
    def __init__(self, index):
        """Initializes the AI with its index and world.
            If you want to store data that is used from turn to turn, put it here."""
        self.index = index
        self.world = None # world is supplied slightly later by the main game

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
            # code go here
        return [(bee.data, bee.action) for bee in bees]