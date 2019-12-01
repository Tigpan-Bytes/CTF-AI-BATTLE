import random
import math
from class_data import *

def get_state_xy(state):
    if state == '0':
        return 0, 1, 'N'
    elif state == '1':
        return 1, 0, 'E'
    elif state == '2':
        return 0, -1, 'S'
    else:
        return -1, 0, 'W'


def compare_lists(a, b):
    same = 0
    for ae in a:
        for be in b:
            if ae == be:
                same = same + 1
    return same == len(a) if len(a) > len(b) else same == len(b)


class AI:
    def __init__(self, index):
        self.world = None
        self.index = index
        self.attacked_hives = [index]
        self.path = None
        self.last_paths = None

    def is_enemy_or_food(self, position, distance):
        tile = self.world.get_tile(position.x, position.y)
        return tile.food or (tile.bee is not None and tile.bee.index != self.index) or (tile.hive and tile.hive_index != self.index)

    def shoot_bee(self, position, distance):
        tile = self.world.get_tile(position.x, position.y)
        return tile.bee is not None and tile.bee.index != self.index

    def shoot_bee_sort(self, position, distance):
        # lower values are sorted first (ex. the priorities [6,3,1,6,7] are sorted to [1,3,6,6,7])
        return self.world.get_tile(position.x, position.y).bee.health * 10 + distance

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
        if len(enemies) == 1:
            if len(enemies[0][1]) != self.last_paths:
                self.path = self.world.breadth_path(enemies[0][1])
                self.last_paths = len(enemies[0][1])
        if len(enemies) == 2:
            if len(enemies[0][1]) + len(enemies[1][1]) != self.last_paths:
                self.path = self.world.breadth_path(enemies[0][1] + enemies[1][1])
                self.last_paths = len(enemies[0][1]) + len(enemies[1][1])
        for bee in bees:
            if bee.data == '':
                bee.data = str(random.randint(0, 3))

            targets = self.world.get_x_in_range(bee.position, self.shoot_bee, 3, self.shoot_bee_sort)
            if len(targets) >= 1:
                bee.action = 'A ' + str(targets[0].x) + ',' + str(targets[0].y)
            elif self.path is not None:
                path = None
                if bee.data == '0' or bee.data == '':
                    path = self.world.breadth_search(bee.position, self.is_enemy_or_food, 16)
                if path is not None and len(path.direction) >= 1:
                    if bee.action_success or random.randint(0, 3) == 0:
                        bee.action = 'M ' + path.direction[0]
                    else:
                        chosen = None
                        for letter in path.direction:
                            if letter != path.direction[0]:
                                chosen = letter
                                break
                        if chosen is None:
                            if path.direction[0] == 'N' or path.direction[0] == 'S':
                                chosen = random.choice(['E', 'W'])
                            else:
                                chosen = random.choice(['N', 'S'])
                        bee.action = 'M ' + chosen
                else:
                    if bee.data == '' or bee.data == '0':
                        bee.data = str(random.randint(0, 3))
                    else:
                        bee.data = str(int(bee.data) - 1)
                    direction = self.path[bee.position]
                    if bee.action_success or random.randint(0, 3) == 0:
                        bee.action = 'M ' + direction
                    else:
                        if direction == 'N' or direction == 'S':
                            bee.action = 'M ' + random.choice(['E', 'W'])
                        else:
                            bee.action = 'M ' + random.choice(['N', 'S'])
            else:
                path = self.world.breadth_search(bee.position, self.is_enemy_or_food, 20)
                if path is not None and len(path.direction) >= 1:
                    if bee.action_success or random.randint(0, 3) == 0:
                        bee.action = 'M ' + path.direction[0]
                    else:
                        chosen = None
                        for letter in path.direction:
                            if letter != path.direction[0]:
                                chosen = letter
                                break
                        if chosen is None:
                            if path.direction[0] == 'N' or path.direction[0] == 'S':
                                chosen = random.choice(['E','W'])
                            else:
                                chosen = random.choice(['N','S'])
                        bee.action = 'M ' + chosen

                else:
                    if not bee.action_success:
                        bee.data = str(random.randint(0, 3))
                    while True:
                        if random.randint(0, 5) == 0:
                            bee.data = str(random.randint(0, 3))
                        xya = get_state_xy(bee.data)
                        if self.world.get_tile(bee.position.x + xya[0], bee.position.y + xya[1]).walkable:
                            bee.action = 'M ' + xya[2]
                            break
                        bee.data = str(random.randint(0, 3))
        return [(bee.data, bee.action) for bee in bees]
