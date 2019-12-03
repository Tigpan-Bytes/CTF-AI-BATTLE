# Grow -> Kill Bot
# Written by Joe Generic
# Member of team: w1nn3r5

import random
import math
from class_data import *

# BEHAVIOR:
# If the turn number is below 150, each bee moves toward the nearest food.
# Otherwise, each bee moves toward the nearest enemy bee.

# KNOWN PROBLEMS:
# 1. This bot doesn't make an attempt to attack enemy hives or bees, and often gets stuck running to their own death.
# 2. This bot is very very slow, even to the point of getting a Timeout error if it grows too big. This happens because
#       each individual bee looks for food or bees, and if that food or bee is very far, it takes a long time to calculate that. Then doing that
#       calculation for 50+ bees is very very slow. You could speed this up greatly by setting distance restrictions on the
#       breadth_searchs. Then doing something else if no path could be found, maybe something with a breadth_path to the enemy hives?
# 3. Currently when the bot is in phase 1 (collect food) many bees all flock toward one piece of food. Wouldn't it be much better
#       to have them split up. You could do this by storing a list (or dictionary) of all the food currently being targeted, then
#       don't have new bees target that tile(change the targeting function so if position is in self.currently_targeted_foods).
# 4. The bot also has a chance of erroring if no food exists (bee.action = 'M ' + path.direction
#       AttributeError: 'NoneType' object has no attribute 'direction', line 76), although this can be easily fixed.
# 5. The 150 turn phase change is very arbitrary, maybe it should be based on bee count or not included at all.
# 6. Overall it is a mediocre bot, although it has a high chance of erroring out because of a timeout error.
#       Surprisingly this bot does better when there are other much more aggressive bots out their to keep its bees
#       in check so it doesn't timeout.

class AI:
    def __init__(self, index):
        """Initializes the AI with its index and world.
            If you want to store data that is used from turn to turn, put it here."""
        self.index = index
        self.world = None # world is supplied slightly later by the main game

    def has_food(self, position, distance):
        """A function passed into self.world.breadth_search to determine if the cell is the end.
            This function just looks for if the tile contains a food"""
        return self.world.get_tile(position.x, position.y).food

    def is_enemy(self, position, distance):
        """A function passed into self.world.breadth_search to determine if the cell is the end.
            This function just looks for if the tile contains a food"""
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

            if turn < 150:
                # if the current turn is less than 300

                path = self.world.breadth_search(bee.position, self.has_food)
                # breadth_search returns a MovePosition position class, with .x and .y of the final position
                # and .direction of the path needed to reach that position
                bee.action = 'M ' + path.direction

                # it looks for the closest piece of food to each bot then moves to collect it
            else:
                path = self.world.breadth_search(bee.position, self.is_enemy)
                # the same, but instead of looking for food, looks for enemy bees
                bee.action = 'M ' + path.direction

        return [(bee.data, bee.action) for bee in bees]