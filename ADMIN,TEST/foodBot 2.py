import random
import math
from class_data import *
TEAM='eee'

def get_state_xy(state):
    if state == '0':
        return 0, 1, 'N'
    elif state == '1':
        return 1, 0, 'E'
    elif state == '2':
        return 0, -1, 'S'
    else:
        return -1, 0, 'W'

class AI:
    def __init__(self, index):
        self.world = None
        self.index = index
        self.attacked_hives = [index]

    def is_enemy_hive(self, position, distance):
        tile = self.world.get_tile(position.x, position.y)
        #return tile.hive_index not in self.attacked_hives
        return tile.food or (tile.bee is not None and tile.bee.index != self.index and distance < 30) or (tile.hive and tile.hive_index != self.index)

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

    def do_turn(self, bees, enemies, turn): # enemies[i][0] is index, enemies[i][1] is hive_positions, enemies[i][2] is bee count
        for bee in bees:
            if bee.data == '':
                bee.data = str(random.randint(0, 3))

            path = self.world.breadth_search(bee.position, self.is_enemy_hive, 30)
            if path is not None and len(path.direction) >= 1:
                bee.action = 'M ' + path.direction[0]
            else:
                while True:
                    if random.randint(0, 5) == 0:
                        bee.data = str(random.randint(0, 3))
                    xya = get_state_xy(bee.data)
                    if self.world.get_tile(bee.position.x + xya[0], bee.position.y + xya[1]).walkable:
                        bee.action = 'M ' + xya[2]
                        break
                    bee.data = str(random.randint(0, 3))
        return [(bee.data, bee.action) for bee in bees]
