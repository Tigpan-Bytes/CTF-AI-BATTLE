# import the pygame module, so you can use it
import pygame

import sys
from contextlib import contextmanager
import threading
import _thread

from os import listdir
from os.path import isfile, join
import importlib

import random
import math

WHITE = (255, 255, 255)
BOARD = (181,169,154)
WALL = (15, 15, 15)
NULL = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 90, 160)

TIMEOUT = 0.1

X_SIZE = 32
Y_SIZE = 32

X_GRIDS = 3
Y_GRIDS = 2


class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


class Tile:
    def __init__(self, walkable, hive=False, hive_index= -1):
        self.walkable = walkable
        self.hive = hive
        self.hive_index = hive_index


class Bot:
    def __init__(self, name, ai, colour):
        self.name = name
        self.terminated = False
        self.ai = ai
        self.position = (32, 32)
        self.hive_colour = colour[0]
        self.bee_colour = colour[1]
        self.hives = []

    def get(self):
        return self


class Board:
    def __init__(self, w, h, bots):
        self.bots = bots
        self.grid = self.create_grid(w, h)
        self.resize_board(math.floor(600 * max(X_SIZE / Y_SIZE, 1)), math.floor(600 * max(Y_SIZE / X_SIZE, 1)))

    def resize_board(self, w, h):
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.cell_size = h / Y_SIZE
        self.x_plus = (w - (self.cell_size * X_SIZE)) / 2

    def render(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, WALL, (self.x_plus, 0, X_SIZE * self.cell_size, Y_SIZE * self.cell_size))

        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                if self.grid[x][y].walkable:
                    if self.grid[x][y].hive:
                        if self.grid[x][y].hive_index == -1:
                            self.grid[x][y].hive = False
                            pygame.draw.rect(self.screen, BOARD,
                                             (x * self.cell_size + self.x_plus, y * self.cell_size,
                                              self.cell_size + 1, self.cell_size + 1))
                        else:
                            pygame.draw.rect(self.screen, self.bots[self.grid[x][y].hive_index].hive_colour,
                                             (x * self.cell_size + self.x_plus - 1, y * self.cell_size - 1,
                                              self.cell_size + 3, self.cell_size + 3))
                    else:
                        pygame.draw.rect(self.screen, BOARD,
                                         (x * self.cell_size + self.x_plus, y * self.cell_size,
                                          self.cell_size + 1, self.cell_size + 1))

    def do_bots(self):
        bot_length = len(self.bots)
        i = 0
        while i < bot_length:
            if not self.bots[i].terminated:
                try:
                    with timeout_limit():
                        self.bots[i].position = self.bots[i].ai.do_turn(self.grid, X_SIZE, Y_SIZE, self.bots[i].position)
                except TimeoutException as e:
                    print('Bot index [' + str(i) + '] (' + self.bots[i].name + ') exceeded timelimit, no actions taken.')
                except Exception as e:
                    print('Bot index [' + str(i) + '] (' + self.bots[i].name + ') did a naughty. Terminating it.')
                    self.bots[i].terminated = True

                pygame.draw.rect(self.screen, self.bots[i].bee_colour,
                                 (self.bots[i].position[0] * self.cell_size + self.x_plus,
                                  self.bots[i].position[1] * self.cell_size,
                                  self.cell_size, self.cell_size))

            i = i + 1

    def create_grid(self, w, h):
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
        i = 0  # index of bots
        for column in range(X_GRIDS):
            for row in range(Y_GRIDS):
                x_index = math.floor(w / X_GRIDS) * column
                y_index = math.floor(h / Y_GRIDS) * row

                for x in range(math.floor(w / X_GRIDS)):
                    for y in range(math.floor(h / Y_GRIDS)):
                        x_i = (x_index + x + w) % w
                        y_i = (y_index + y + h) % h
                        grid[x_i][y_i] = Tile(grid_part[x][y].walkable, grid_part[x][y].hive, i if i < len(self.bots) else -1)
                i = i + 1
        print(w * h)
        return grid

    def update(self):
        self.render()
        self.do_bots()


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
    colours = [[(255, 100, 100), (235, 80, 80)], [(100, 255, 100), (80, 235, 80)], [(100, 100, 255), (80, 80, 235)],
               [(255, 170, 130), (235, 150, 110)], [(170, 255, 130), (150, 235, 110)],
               [(255, 130, 170), (235, 110, 150)], [(170, 130, 255), (150, 110, 235)],
               [(130, 255, 170), (110, 235, 150)], [(130, 170, 255), (110, 150, 235)],
               [(255, 255, 120), (235, 235, 100)], [(255, 120, 255), (235, 100, 235)],
               [(120, 255, 255), (100, 235, 235)]]
    random.shuffle(colours)

    bot_path = './bots'

    bot_names = [f[0:-3] for f in listdir(bot_path) if isfile(join(bot_path, f))]
    bot_ais = [importlib.import_module('bots.' + f).AI(X_SIZE, Y_SIZE) for f in bot_names]

    return [Bot(n, a, c) for n, a, c in zip(bot_names, bot_ais, colours)]


def main():
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")

    board = Board(X_SIZE, Y_SIZE, get_bots())

    while True:
        board.update()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                board.resize_board(event.w, event.h)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    X_SIZE *= X_GRIDS
    Y_SIZE *= Y_GRIDS
    main()
