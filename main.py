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

TIMEOUT = 0.2
X_SIZE = 30
Y_SIZE = 30

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

def create_grid(w, h):
    return [[random.getrandbits(2) == 0 for x in range(w)] for y in range(h)]

def resize_board(w, h):
    return math.floor(h / Y_SIZE)

def main():
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")

    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    cell_size = resize_board(600, 600)
    grid = create_grid(X_SIZE, Y_SIZE)

    bot_path = './bots'

    bot_names = [f[0:-3] for f in listdir(bot_path) if isfile(join(bot_path, f))]
    bot_modules = [importlib.import_module('bots.' + f) for f in bot_names]
    bots = [ai.AI() for ai in bot_modules]
    bots_position = [(random.randrange(0, 20), random.randrange(0, 20)) for _ in bot_modules]

    while True:
        screen.fill(WHITE)
        pygame.draw.rect(screen, BOARD, (0, 0, X_SIZE * cell_size, Y_SIZE * cell_size))
        
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                if grid[x][y]:
                    pygame.draw.rect(screen, BLACK, (x * cell_size, y * cell_size, cell_size - 1, cell_size - 1))
        
        bot_length = len(bots)
        i = 0
        while i < bot_length:
            try:
                with timeout_limit():
                    bots_position[i] = bots[i].do_turn(bots_position[i])
            except TimeoutException as e:
                print('Bot index [' + str(i) + '] ('+bot_names[i]+') exceeded timelimit, no actions taken.')
            except Exception as e:
                print('Bot index [' + str(i) + '] ('+bot_names[i]+') did a naughty. Terminating it.')
                
                bots.pop(i)
                bot_names.pop(i)
                bots_position.pop(i)
                
                i = i - 1
                bot_length = bot_length-1
                
            pygame.draw.rect(screen, RED, (bots_position[i][0] * cell_size, bots_position[i][1] * cell_size, cell_size - 1, cell_size - 1))
            
            i = i + 1


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                cell_size = resize_board(event.w, event.h)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    main()
