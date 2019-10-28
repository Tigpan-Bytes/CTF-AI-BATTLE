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

CELL_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

TIMEOUT = 0.5

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(msg='', seconds=TIMEOUT):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()

class Tile:
    def __init__(self, position):
        self.position = position
        self.state = random.getrandbits(1)
        self.nextState = False

    def set_next(self, neighbors):
        alive_count = 0
        for cell in neighbors:
            if cell is None:
                continue
            alive_count += cell.state
        if self.state:
            self.nextState = 1 < alive_count < 4
        else:
            self.nextState = alive_count == 3


def get_2d_tile_array(rows, cols):
    returnable = [[Tile((x, y)) for x in range(rows)] for y in range(cols)]
    return returnable


def get_2d_element(arr, position):
    if position[0] < 0 or position[1] < 0:
        return None
    if position[0] >= len(arr) or position[1] >= len(arr[0]):
        return None

    return arr[position[0]][position[1]]


def get_neighbors(arr, pos):
    return [get_2d_element(arr, (pos[0] - 1, pos[1] - 1)), get_2d_element(arr, (pos[0] - 1, pos[1])),
            get_2d_element(arr, (pos[0] - 1, pos[1] + 1)),
            get_2d_element(arr, (pos[0], pos[1] - 1)), get_2d_element(arr, (pos[0], pos[1] + 1)),
            get_2d_element(arr, (pos[0] + 1, pos[1] - 1)), get_2d_element(arr, (pos[0] + 1, pos[1])),
            get_2d_element(arr, (pos[0] + 1, pos[1] + 1))]


def rebuild_array():
    w, h = pygame.display.get_surface().get_size()
    return get_2d_tile_array(math.floor(h / CELL_SIZE), math.floor(w / CELL_SIZE))


def main():
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")

    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    arr = rebuild_array()

    bot_path = './bots'

    bot_imports = [f for f in listdir(bot_path) if isfile(join(bot_path, f))]
    bot_modules = [importlib.import_module('bots.' + f[0:-3]) for f in bot_imports]
    bots = [(ai.AI()) for ai in bot_modules]
    bots_position = [(random.randrange(0, 20), random.randrange(0, 20)) for _ in bot_modules]

    while True:
        screen.fill(WHITE)

        for x in range(len(arr)):
            for y in range(len(arr[0])):
                arr[x][y].set_next(get_neighbors(arr, (x, y)))

        for x in range(len(arr)):
            for y in range(len(arr[0])):
                arr[x][y].state = arr[x][y].nextState

        for x in range(len(arr)):
            for y in range(len(arr[0])):
                pygame.draw.rect(screen, BLACK if arr[x][y].state else WHITE,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

        for i in range(len(bots)):
            try:
                with time_limit("Time limit exceeded"):
                    bots_position[i] = bots[i].do_turn(bots_position[i])
            except TimeoutException as e:
                print(e)
            except Exception as e:
                print('Your bot did a naughty')

            pygame.draw.rect(screen, RED, (bots_position[i][0] * CELL_SIZE, bots_position[i][1] * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                arr = rebuild_array()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    main()
