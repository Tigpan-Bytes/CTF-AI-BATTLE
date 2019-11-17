class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Tile:
    def __init__(self, walkable, hive=False, hive_index=-1):
        self.walkable = walkable
        self.hive = hive
        self.hive_index = hive_index


class Bot:
    def __init__(self, name, ai, colour):
        self.name = name
        self.terminated = False
        self.ai = ai
        self.hive_colour = (max(colour[0] - 40, 0), max(colour[1] - 40, 0), max(colour[2] - 40, 0))
        self.colour = colour
        self.hives = []
        self.bees = []


class Bee:
    def __init__(self, position, health=4, data=''):
        self.health = health
        self.position = position
        self.data = data


class BeeUnit:
    def __init__(self, position, health, data):
        self.health = health
        self.position = position
        self.data = data
        self.action = ''


class World:
    def __init__(self, width, height, tiles):
        self.width = width
        self.height = height
        self.tiles = tiles

    def get_tile(self, x, y):
        return self.tiles[x % self.width][y % self.height]

    def copy(self):
        return World(self.width, self.height, self.tiles.copy())