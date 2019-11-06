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
BOARD = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

TIMEOUT = 0.1
X_SIZE = 60
Y_SIZE = 60

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        
class Bot():
    def __init__(self, name, ai):
        self.name = name
        self.ai = ai
        self.position = (random.randrange(0, 20), random.randrange(0, 20))
        
class Board():
    def __init__(self, w, h, bots):
        self.grid = create_grid(w, h)
        self.resize_board(600, 600)
        self.bots = bots
        
    def resize_board(self, w, h):
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.cell_size = h / Y_SIZE
        self.x_plus = (w - (self.cell_size * X_SIZE)) / 2
        
    def render(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, BOARD, (self.x_plus, 0, X_SIZE * self.cell_size, Y_SIZE * self.cell_size))
        
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                if not self.grid[x][y]:
                    pygame.draw.rect(self.screen, BLACK, (x * self.cell_size + self.x_plus, y * self.cell_size,
                                                          self.cell_size + 1, self.cell_size + 1))
                    
    def do_bots(self):
        bot_length = len(self.bots)
        i = 0
        while i < bot_length:
            try:
                with timeout_limit():
                    self.bots[i].position = self.bots[i].ai.do_turn(self.bots[i].position)
            except TimeoutException as e:
                print('Bot index [' + str(i) + '] ('+self.bots[i].name+') exceeded timelimit, no actions taken.')
            except Exception as e:
                print('Bot index [' + str(i) + '] ('+self.bots[i].name+') did a naughty. Terminating it.')
                
                self.bots.pop(i)

                i = i - 1
                bot_length = bot_length - 1
                
            pygame.draw.rect(self.screen, RED, (self.bots[i].position[0] * self.cell_size + self.x_plus,
                                                self.bots[i].position[1] * self.cell_size,
                                                self.cell_size - 1, self.cell_size - 1))
            
            i = i + 1
                    
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

def insert_grid(grid, quarter, w, h, x_index, y_index):
    for x in range(math.floor(w / 2)):
        for y in range(math.floor(h / 2)):
            grid[(x_index + x) % w][(y_index + y) % h] = quarter[x][y]
    return grid

def create_grid(w, h):
    grid_quarter = [[False for y in range(math.floor(h / 2))] for x in range(math.floor(w / 2))]
    grid_quarter_pattern = [[False,False,False,False,False,False],
                            [True, True, True, False, True, False],
                            [True, False, True, True, True, False],
                            [False,False,True, True, False,False],
                            [False, True, True, True, False, True],
                            [False, True,False, True, True, True]]
    for x in range(math.floor(w / 2)):
        for y in range(math.floor(h / 2)):
            if grid_quarter_pattern[math.floor(y / 5 - h / 24) % 6][math.floor(x / 5) % 6]:
                grid_quarter[x][y] = True
    grid_quarter = randomize_grid(grid_quarter, math.floor(w / 2), math.floor(h / 2))

    grid = [[False for y in range(h)] for x in range(w)]
    grid = insert_grid(grid, grid_quarter, w, h, 0, 0)
    grid = insert_grid(grid, grid_quarter, w, h, math.floor(w / 2), math.floor(h / 4))
    grid = insert_grid(grid, grid_quarter, w, h, 0, math.floor(h / 2))
    grid = insert_grid(grid, grid_quarter, w, h, math.floor(w / 2), math.floor((3 * h) / 4))
    return grid

def randomize_grid(grid, w, h):
    for x in range(w):
        for y in range(h):
            if random.randrange(0, 100) < 25:
                grid[x][y] = not grid[x][y]

    for _ in range(5):
        grid_count = [[random.randrange(0, 100) < 45 for y in range(h)] for x in range(w)]
        for x in range(w):
            for y in range(h):
                count = -1 if grid[x][y] else 0;
                for x_plus in [-1, 0, 1]:
                    for y_plus in [-1, 0, 1]:
                        if x + x_plus >= 0 and y + y_plus >= 0 and x + x_plus < w and y + y_plus < h:
                            count += 1 if grid[x + x_plus][y + y_plus] else 0
                        else:
                            if x + x_plus < 0:
                                count += 1 if grid[w - 1][(y + y_plus - math.floor(h / 2)) % h] else 0
                            else:
                                count += 1 if grid[0][(y + y_plus + math.floor(h / 2)) % h] else 0
                grid_count[x][y] = count
        for x in range(w):
            for y in range(h):
                if grid[x][y]:
                    grid[x][y] = grid_count[x][y] >= 4
                else:
                    grid[x][y] = grid_count[x][y] >= 5
    return grid

def get_bots():
    bot_path = './bots'

    bot_names = [f[0:-3] for f in listdir(bot_path) if isfile(join(bot_path, f))]
    bot_ais = [importlib.import_module('bots.' + f).AI(X_SIZE, Y_SIZE) for f in bot_names]
    
    return [Bot(n, a) for n, a in zip(bot_names, bot_ais)]

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
    main()
