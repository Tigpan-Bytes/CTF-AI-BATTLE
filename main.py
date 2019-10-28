# import the pygame module, so you can use it
import pygame, sys
from os import listdir
from os.path import isfile, join
import importlib
import random
import math

from .bots import randomBot

CELL_SIZE = 20

class Tile:
    def __init__(self, position):
        self.position = position
        self.state = random.getrandbits(1)
        self.nextState = False

    def setNext(self, neighbors):
        alive_count = 0
        for cell in neighbors:
                if cell == None:
                    continue
                alive_count += cell.state
        if self.state:
            self.nextState = alive_count > 1 and alive_count < 4
        else:
            self.nextState = alive_count == 3
        

def get2dTileArray(rows, cols):
    returnable = [[Tile((x, y)) for x in range(rows)] for y in range(cols)]
    return returnable

                
def get2dElement(arr, position):
    if position[0] < 0 or position[1] < 0:
        return None
    if position[0] >= len(arr) or position[1] >= len(arr[0]):
        return None
    
    return arr[position[0]][position[1]]

def getNeighbors(arr, pos):
    return [get2dElement(arr, (pos[0] - 1, pos[1] - 1)), get2dElement(arr, (pos[0] - 1, pos[1])), get2dElement(arr, (pos[0] - 1, pos[1] + 1)),
            get2dElement(arr, (pos[0],     pos[1] - 1)),                                          get2dElement(arr, (pos[0], pos[1] + 1)),
            get2dElement(arr, (pos[0] + 1, pos[1] - 1)), get2dElement(arr, (pos[0] + 1, pos[1])), get2dElement(arr, (pos[0] + 1, pos[1] + 1))]

def rebuildArray():
    w, h = pygame.display.get_surface().get_size()
    return get2dTileArray(math.floor(h / CELL_SIZE), math.floor(w / CELL_SIZE))
 
# define a main function
def main():
     
    # initialize the pygame module
    pygame.init()
    pygame.display.set_caption("CTF: Bee Swarm Battle")
     
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    arr = rebuildArray()

    bot_path = './bots'

    bot_imports = [f for f in listdir(bot_path) if isfile(join(bot_path, f))]
    #bot_imports.remove('__init__.py')
    bot_ais = [__import__('bots.' + f[0:-3]) for f in bot_imports]
    print(bot_ais)
    dir(bot_ais)
    bots = [((random.randrange(0, 30), random.randrange(0, 30)), ai.AI()) for ai in bot_ais]
    import <'.bots.randomBot'>
     
    # define a variable to control the main loop
    WHITE=(255,255,255)
    BLACK=(0,0,0)
    RED=(255,0,0)
     
    # main loop
    while True:
        # event handling, gets all event from the event queue
        
        screen.fill(WHITE)
        
        for x in range(len(arr)):
            for y in range(len(arr[0])):
                arr[x][y].setNext(getNeighbors(arr, (x, y)))
                
        for x in range(len(arr)):
            for y in range(len(arr[0])):
                arr[x][y].state = arr[x][y].nextState
        
        for x in range(len(arr)):
            for y in range(len(arr[0])):
                pygame.draw.rect(screen, BLACK if arr[x][y].state else WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
                
        for bot in bots:
            bot[0] = bot[1].do_turn(bot[0])
            pygame.draw.rect(screen, RED, (bot[0][0] * CELL_SIZE, bot[0][1] * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
    
        pygame.display.update()  
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                arr = rebuildArray()
        
        #pygame.time.wait(200)
     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()