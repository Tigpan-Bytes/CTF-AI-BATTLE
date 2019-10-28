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
        raise TimeoutException(msg)
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


def main():
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")

    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)

    bot_path = './bots'

    bot_imports = [f for f in listdir(bot_path) if isfile(join(bot_path, f))]
    bot_modules = [importlib.import_module('bots.' + f[0:-3]) for f in bot_imports]
    bots = [(ai.AI()) for ai in bot_modules]
    bots_position = [(random.randrange(0, 20), random.randrange(0, 20)) for _ in bot_modules]

    while True:
        screen.fill(WHITE)

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


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    main()
