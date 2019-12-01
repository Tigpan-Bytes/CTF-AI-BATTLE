import random
import math
from class_data import *

class AI:
    def __init__(self, index):
        self.world = None
        self.index = index

    def update_tiles(self, food_changes, bee_changes, lost_hive_changes):
        """It is not recommended to change this function unless you are ABSOLUTELY sure you know what you are doing.
        This is called once before asking for actions with all the data from the previous round. Then again if a bot was terminated
        containing only the data for the terminated bots (bots that had a runtime error)."""
        for change in food_changes:
            self.world.get_tile(change[1], change[2]).food = change[0]
        for change in bee_changes:
            self.world.get_tile(change[1], change[2]).bee = change[0]
        for change in lost_hive_changes:
            self.world.get_tile(change.x, change.y).hive = False
            self.world.get_tile(change.x, change.y).hive_index = -1

    def do_turn(self, bees, enemies): # enemies[i][0] is index, enemies[i][1] is hive_positions, enemies[i][2] is bee count
        self.world.tiles[random.randint(0, 15)][random.randint(0, 15)] = None
        for bee in bees:
            bee.position = Position(bee.position.x + 1, bee.position.y + 1)
            bee.action = "M N"
        return [(bee.data, bee.action) for bee in bees]
