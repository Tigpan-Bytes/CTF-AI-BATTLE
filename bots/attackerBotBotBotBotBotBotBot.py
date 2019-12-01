import random
import math
from class_data import *


class AI:
    def __init__(self, index):
        self.world = None
        self.index = index

    def is_enemy_hive(self, position, distance):
        tile = self.world.get_tile(position.x, position.y)
        return tile.hive and tile.hive_index != self.index

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
        for bee in bees:
            if random.randint(0, 10) == 0:
                bee.action = 'M ' + random.choice(['N','E','S','W'])
            else:
                path = self.world.breadth_search(bee.position, self.is_enemy_hive)
                if path is not None and len(path.direction) >= 1:
                    bee.action = 'M ' + path.direction[0]
        return [(bee.data, bee.action) for bee in bees]
