# import the pygame module, so you can use it
import _thread
import importlib
import math
import traceback
import random
import sys
import threading
from contextlib import contextmanager
from os import listdir
from os.path import isfile, join

import pygame
from class_data import *

WHITE = (255, 255, 255)
BOARD = (191,174,158)
FOOD = (207,230,140)
WALL = (15, 15, 15)
BLACK = (0, 0, 0)

TIMEOUT = 0.1

X_SIZE = 32
Y_SIZE = 32

X_GRIDS = 3
Y_GRIDS = 3

X_GRID_SIZE = X_SIZE
Y_GRID_SIZE = Y_SIZE

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def timeout_limit(seconds=TIMEOUT):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


class Game:
    def __init__(self, w, h):
        self.world = World(w, h, create_grid(w, h))
        self.bots = get_bots()
        self.world.tiles = self.set_hives(w, h, self.world.tiles)
        self.world.generate_neighbors()
        self.resize_board(math.floor(600 * max(X_SIZE / Y_SIZE, 1)), math.floor(600 * max(Y_SIZE / X_SIZE, 1)))

        self.turn = 0
        self.food_changes = []
        self.bee_changes = []

        for _ in range(3):
            self.place_food()

        for bot in self.bots:
            bot.ai.world = self.world.copy()

    def resize_board(self, w, h):
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.cell_size = h / Y_SIZE
        self.half_cell = self.cell_size / 2
        self.x_plus = (w - (self.cell_size * X_SIZE)) / 2

    def render(self):
        self.screen.fill(WHITE)
        
        if self.turn & 7 == 0: # if turn % 8 == 0
            self.place_food()
            
        pygame.draw.rect(self.screen, WALL, (self.x_plus, 0, X_SIZE * self.cell_size, Y_SIZE * self.cell_size))

        hives = []
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                tile = self.world.get_tile(x,y)
                if tile.walkable:
                    if tile.hive:
                        if tile.hive_index == -1:
                            tile.hive = False
                            pygame.draw.rect(self.screen, FOOD if tile.food else BOARD,
                                             (x * self.cell_size + self.x_plus, (Y_SIZE - 1) * self.cell_size - y * self.cell_size,
                                              self.cell_size + 1, self.cell_size + 1))
                        else:
                            hives.append([x, y, self.bots[tile.hive_index].hive_colour])
                    else:
                        pygame.draw.rect(self.screen, FOOD if tile.food else BOARD,
                                         (x * self.cell_size + self.x_plus, (Y_SIZE - 1) * self.cell_size - y * self.cell_size,
                                          self.cell_size + 1, self.cell_size + 1))
        for hive in hives:
            pygame.draw.rect(self.screen, BLACK,
                             (hive[0] * self.cell_size + self.x_plus - 2, (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size - 2,
                              self.cell_size + 5, self.cell_size + 5))
            pygame.draw.rect(self.screen, hive[2],
                             (hive[0] * self.cell_size + self.x_plus, (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size,
                              self.cell_size + 1, self.cell_size + 1))

    def do_bees_actions(self, bees):
        for bee in bees:
            if len(bee.action) >= 3:
                action = bee.action[0]
                self.world.tiles[bee.position.x][bee.position.y].bee = None
                self.bee_changes.append((None, bee.position.x, bee.position.y))
                if action == 'M':
                    x = get_dir_x(bee.action[2])
                    y = get_dir_y(bee.action[2])
                    
                    tile = self.world.get_tile(bee.position.x + x, bee.position.y + y)
                    if tile.walkable and tile.bee is None:
                        bee.position = Position((bee.position.x + x) % X_SIZE, (bee.position.y + y) % Y_SIZE)
                        
                    bee.action = ''
                self.world.tiles[bee.position.x][bee.position.y].bee = bee
                self.bee_changes.append((bee.copy(), bee.position.x, bee.position.y))
            if self.world.tiles[bee.position.x][bee.position.y].food:
                self.food_changes.append((False, bee.position.x, bee.position.y))
                self.world.tiles[bee.position.x][bee.position.y].food = False

    def do_bots(self):
        # change world to be saved by bots and before getting their turn, update the food and bee
        bot_length = len(self.bots)

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated:
                try:
                    with timeout_limit():
                        self.bots[i].ai.update_tiles(self.food_changes.copy(), self.bee_changes.copy())
                        data_actions = self.bots[i].ai.do_turn([bee.copy() for bee in self.bots[i].bees])
                        for d_a, j in zip(data_actions, range(len(self.bots[i].bees))):
                            self.bots[i].bees[j].data = d_a[0]
                            self.bots[i].bees[j].action = d_a[1]
                except TimeoutException as e:
                    print('Turn ' + str(self.turn) + ': Bot index [' + str(i) + '] (' + self.bots[i].name + ') exceeded timelimit, no actions taken.')
                except Exception:
                    print('Turn ' + str(self.turn) + ': Bot index [' + str(i) + '] (' + self.bots[i].name + ') did a naughty. Terminating it.')
                    print(" > Naughty details:", traceback.format_exc())

                    self.bots[i].terminated = True
                    for bee in self.bots[i].bees:
                        self.bee_changes.append((None, bee.position.x, bee.position.y))
                        self.world.tiles[bee.position.x][bee.position.y].bee = None
                    self.bots[i].bees = []
                    for hive in self.bots[i].hives:
                        hive.hive = False
                        hive.hive_index = -1
                    self.bots[i].hives = []
            i = i + 1

        self.food_changes = []
        self.bee_changes = []
        i = 0
        while i < bot_length:
            if not self.bots[i].terminated:
                self.do_bees_actions(self.bots[i].bees)
            i = i + 1

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated:
                for bee in self.bots[i].bees:
                    pygame.draw.polygon(self.screen, self.bots[i].colour,
                                        [(bee.position.x * self.cell_size + self.x_plus + 1,
                                          (Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.half_cell),
                                         (bee.position.x * self.cell_size + self.x_plus + self.half_cell,
                                          (Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + 1),
                                         (bee.position.x * self.cell_size + self.x_plus + self.cell_size - 1,
                                          (Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.half_cell),
                                         (bee.position.x * self.cell_size + self.x_plus + self.half_cell,
                                          (Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.cell_size - 1)])

            i = i + 1
        self.turn = self.turn + 1
        
    def place_food(self):
        skips = random.randint(0, 20)
        x = random.randint(0, X_GRID_SIZE - 1)
        y = random.randint(0, Y_GRID_SIZE - 1)
        while True:
            tile = self.world.get_tile(x,y)
            if tile.walkable and not tile.was_hive:
                if skips == 0:
                    break
                else:
                    skips = skips - 1
            x = x + 1
            if x >= X_GRID_SIZE:
                x = 0
                y = y + 1
                if y >= Y_GRID_SIZE:
                    y = 0
        
        for x_g in range(X_GRIDS):
            for y_g in range(Y_GRIDS):
                self.food_changes.append((True, x + x_g * X_GRID_SIZE, y + y_g * Y_GRID_SIZE))
                self.world.tiles[x + x_g * X_GRID_SIZE][y + y_g * Y_GRID_SIZE].food = True
    
    def set_hives(self, w, h, grid):
        i = 0  # index of bots
        for column in range(X_GRIDS):
            for row in range(Y_GRIDS):
                x_index = math.floor(w / X_GRIDS) * column
                y_index = math.floor(h / Y_GRIDS) * row

                for x in range(math.floor(w / X_GRIDS)):
                    for y in range(math.floor(h / Y_GRIDS)):
                        x_i = (x_index + x + w) % w
                        y_i = (y_index + y + h) % h
                        index = i if i < len(self.bots) else -1
                        if index == -1:
                            grid[x_i][y_i].hive = False
                        if grid[x_i][y_i].hive:
                            grid[x_i][y_i].hive_index = index
                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i)))
                            self.world.tiles[x_i][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i + 1, y_i)))
                            self.world.tiles[x_i + 1][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i + 1)))
                            self.world.tiles[x_i][y_i + 1].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i - 1, y_i)))
                            self.world.tiles[x_i - 1][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i - 1)))
                            self.world.tiles[x_i][y_i - 1].bee = self.bots[i].bees[-1]
                            self.bots[grid[x_i][y_i].hive_index].hives.append(grid[x_i][y_i])
                i = i + 1
        return grid

    def update(self):
        self.render()
        self.do_bots()
        
def get_dir_x(dir):
    if dir == 'E':
        return 1
    if dir == 'W':
        return -1
    return 0

def get_dir_y(dir):
    if dir == 'N':
        return 1
    if dir == 'S':
        return -1
    return 0

def create_grid(w, h):
    grid_partial_pattern = [[2, 1, 3, 3, 0, 3, 3, 3, 3, 0, 1, 2],
                            [1, 2, 1, 3, 0, 2, 2, 1, 1, 2, 2, 1],
                            [3, 1, 2, 2, 2, 1, 0, 2, 2, 1, 1, 3],
                            [3, 3, 1, 1, 2, 1, 3, 0, 2, 3, 3, 3],
                            [0, 3, 3, 3, 1, 2, 0, 3, 2, 2, 1, 3],
                            [0, 2, 2, 3, 3, 2, 1, 3, 1, 'A', 2, 3],
                            [3, 2, 'B', 1, 3, 1, 2, 3, 3, 2, 2, 0],
                            [3, 1, 2, 2, 3, 0, 2, 1, 3, 3, 3, 0],
                            [3, 3, 3, 2, 0, 3, 1, 2, 1, 1, 3, 3],
                            [3, 1, 1, 2, 2, 0, 1, 2, 2, 2, 1, 3],
                            [1, 2, 2, 1, 1, 2, 2, 0, 3, 1, 2, 1],
                            [2, 1, 0, 3, 3, 3, 3, 0, 3, 3, 1, 2]]

    # slight randomization
    if random.getrandbits(1) == 1:
        grid_partial_pattern.reverse()
    if random.getrandbits(1) == 1:
        # Rotates array 90 degrees
        grid_partial_pattern = list(zip(*grid_partial_pattern[::-1]))

    grid_template = [[0 for y in range(math.floor(h / Y_GRIDS))] for x in range(math.floor(w / X_GRIDS))]

    # places the template into the correct format
    for x in range(math.floor(w / X_GRIDS)):
        for y in range(math.floor(h / Y_GRIDS)):
            grid_template[x][y] = grid_partial_pattern[math.floor(y / (h / (Y_GRIDS * 12))) % 12][
                math.floor(x / (w / (X_GRIDS * 12))) % 12]
    grid_part = randomize_grid(grid_template, math.floor(w / X_GRIDS), math.floor(h / Y_GRIDS))

    # checks if the grid is valid
    grid_part = None
    while not verify_grid(grid_part, math.floor(w / X_GRIDS), math.floor(h / Y_GRIDS)):
        grid_template = [[0 for y in range(math.floor(h / Y_GRIDS))] for x in range(math.floor(w / X_GRIDS))]

        for x in range(math.floor(w / X_GRIDS)):
            for y in range(math.floor(h / Y_GRIDS)):
                grid_template[x][y] = grid_partial_pattern[math.floor(y / (h / (Y_GRIDS * 12))) % 12][
                    math.floor(x / (w / (X_GRIDS * 12))) % 12]
        grid_part = randomize_grid(grid_template, math.floor(w / X_GRIDS), math.floor(h / Y_GRIDS))

    # places the grid tile in the main grid
    grid = [[None for y in range(h)] for x in range(w)]
    for column in range(X_GRIDS):
        for row in range(Y_GRIDS):
            x_index = math.floor(w / X_GRIDS) * column
            y_index = math.floor(h / Y_GRIDS) * row

            for x in range(math.floor(w / X_GRIDS)):
                for y in range(math.floor(h / Y_GRIDS)):
                    x_i = (x_index + x + w) % w
                    y_i = (y_index + y + h) % h
                    grid[x_i][y_i] = Tile(grid_part[x][y].walkable,
                                          grid_part[x][y].hive,
                                          grid_part[x][y].hive,
                                          -1)

    return grid


def verify_grid(grid, w, h):
    if grid == None:
        return False

    grid_walked = [[False for y in range(h)] for x in range(w)]
    position = [-1, -1]
    for x in range(w):
        for y in range(h):
            if grid[x][y].walkable:
                position = [x, y]
                break
        if position[0] != -1:
            break
    positions = [position]
    grid_walked[position[0]][position[1]] = True

    while len(positions) > 0:
        pos = positions.pop(0)
        if pos[0] > 0 and not grid_walked[pos[0] - 1][pos[1]] and grid[pos[0] - 1][pos[1]].walkable:
            grid_walked[pos[0] - 1][pos[1]] = True
            positions.append([pos[0] - 1, pos[1]])
        if pos[0] < w - 1 and not grid_walked[pos[0] + 1][pos[1]] and grid[pos[0] + 1][pos[1]].walkable:
            grid_walked[pos[0] + 1][pos[1]] = True
            positions.append([pos[0] + 1, pos[1]])
        if pos[1] > 0 and not grid_walked[pos[0]][pos[1] - 1] and grid[pos[0]][pos[1] - 1].walkable:
            grid_walked[pos[0]][pos[1] - 1] = True
            positions.append([pos[0], pos[1] - 1])
        if pos[1] < h - 1 and not grid_walked[pos[0]][pos[1] + 1] and grid[pos[0]][pos[1] + 1].walkable:
            grid_walked[pos[0]][pos[1] + 1] = True
            positions.append([pos[0], pos[1] + 1])

    reached_top = False
    reached_left = False
    reached_right = False
    reached_bottom = False
    hive_count = 0

    for x in range(w):
        for y in range(h):
            if x == 0 and grid_walked[x][y]:
                reached_left = True
            if x == w - 1 and grid_walked[x][y]:
                reached_right = True
            if y == 0 and grid_walked[x][y]:
                reached_top = True
            if y == h - 1 and grid_walked[x][y]:
                reached_bottom = True
            if grid_walked[x][y] and grid[x][y].hive:
                hive_count = hive_count + 1

    return reached_top and reached_left and reached_right and reached_bottom and hive_count == 2


def randomize_grid(grid_template, w, h):
    grid = [[Tile(False) for y in range(h)] for x in range(w)]
    grid_a = []
    grid_b = []
    for x in range(w):
        for y in range(h):
            if grid_template[x][y] == 'A':
                grid_a.append([x, y])
                grid[x][y].walkable = random.randrange(0, 100) < 70
            elif grid_template[x][y] == 'B':
                grid_b.append([x, y])
                grid[x][y].walkable = random.randrange(0, 100) < 70
            elif grid_template[x][y] == 2:
                grid[x][y].walkable = random.randrange(0, 100) < 85
            elif grid_template[x][y] == 3:
                grid[x][y].walkable = random.randrange(0, 100) < 10
            elif random.randrange(0, 100) < 30:
                grid[x][y].walkable = not grid_template[x][y]
            else:
                grid[x][y].walkable = grid_template[x][y]

    a_index = grid_a[random.randint(0, len(grid_a) - 1)]
    b_index = grid_b[random.randint(0, len(grid_b) - 1)]

    grid[a_index[0]][a_index[1]].hive = True
    grid[a_index[0]][a_index[1]].walkable = True

    grid[b_index[0]][b_index[1]].hive = True
    grid[b_index[0]][b_index[1]].walkable = True

    for _ in range(4):
        grid_count = [[10 for y in range(h)] for x in range(w)]
        for x in range(w):
            for y in range(h):
                if grid[x][y].hive:  # hive is always walkable
                    continue
                count = -1 if grid[x][y].walkable else 0
                for x_plus in [-1, 0, 1]:
                    for y_plus in [-1, 0, 1]:
                        if grid[(x + x_plus) % w][(y + y_plus) % h].hive:
                            count = 10
                            break
                        count += 1 if grid[(x + x_plus) % w][(y + y_plus) % h].walkable else 0
                grid_count[x][y] = count
        for x in range(w):
            for y in range(h):
                if grid[x][y].walkable:
                    grid[x][y].walkable = grid_count[x][y] >= 4
                else:
                    grid[x][y].walkable = grid_count[x][y] >= 5
    return grid


def get_bots():
    colours = [(255,100,255), (0,117,220), (153,63,0), (50,50,60), (0,92,49), (0,255,0), (255,255,255), (128,128,128),
               (148,255,181), (113,94,0), (183,224,10), (194,0,136), (0,51,128), (203,121,5), (255,0,16),
               (112,255,255), (0,153,143), (255,255,0), (116,10,255), (90,0,0), (255,80,5)]
    random.shuffle(colours)

    bot_path = './bots'

    bot_names = [f[0:-3] for f in listdir(bot_path) if isfile(join(bot_path, f))]
    random.shuffle(bot_names)
    bots = []
    for i in range(len(bot_names)):
        try:
            bot_ai = importlib.import_module('bots.' + bot_names[i]).AI(i)
            bots.append(Bot(bot_names[i], bot_ai, colours.pop(0)))
        except Exception:
            print('Start: Bot (' + bot_names[i] + ') did a naughty during creation. Not including it.')
            print(" > Naughty details:", traceback.format_exc())
    return bots


def main():
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")

    game = Game(X_SIZE, Y_SIZE)

    while True:
        game.update()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                game.resize_board(event.w, event.h)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    X_SIZE *= X_GRIDS
    Y_SIZE *= Y_GRIDS
    main()
