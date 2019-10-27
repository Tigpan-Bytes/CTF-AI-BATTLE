# import the pygame module, so you can use it
import pygame, sys
import random
import math

CELL_SIZE = 20

def get2dArray(rows, cols):
    return [[FALSE for x in range(rows)] for y in range(cols)]

def rebuildArray():
    w, h = pygame.display.get_surface().get_size()
    return get2dArray(math.floor(w / CELL_SIZE), math.floor(h / CELL_SIZE))
 
# define a main function
def main():
     
    # initialize the pygame module
    pygame.init()
    pygame.display.set_caption("minimal program")
     
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    arr = rebuildArray()
     
    # define a variable to control the main loop
    WHITE=(255,255,255)
    BLUE=(0,0,255)
     
    # main loop
    while True:
        # event handling, gets all event from the event queue
        
        screen.fill(WHITE)
        
        w, h = pygame.display.get_surface().get_size()
        for x in range(w):
            for y in range(h):
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
    
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
     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()