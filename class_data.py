from collections import deque
import heapq


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


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MovePosition:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

class MoveCostPosition:
    def __init__(self, x, y, direction, priority):
        self.x = x
        self.y = y
        self.direction = direction
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority


class Queue:
    def __init__(self):
        self.elements = deque()

    def empty(self):
        return len(self.elements) == 0

    def enqueue(self, x):
        self.elements.append(x)

    def dequeue(self):
        return self.elements.popleft()

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def enqueue(self, item):
        heapq.heappush(self.elements, item)

    def dequeue(self):
        return heapq.heappop(self.elements)


class World:
    def __init__(self, width, height, tiles):
        self.width = width
        self.half_width = int(width / 2)
        self.height = height
        self.half_height = int(height / 2)
        self.tiles = tiles

    def generate_neighbors(self):
        neighbors = [[[] for y in range(self.height)] for x in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                directions = []
                cell = self.get_tile(x, y)
                if not cell.walkable:
                    continue
                if (x + y) & 1 == 0:
                    if self.get_tile(x, y + 1).walkable:
                        directions.append((0, 1))
                    if self.get_tile(x, y - 1).walkable:
                        directions.append((0, -1))
                    if self.get_tile(x + 1, y).walkable:
                        directions.append((1, 0))
                    if self.get_tile(x - 1, y).walkable:
                        directions.append((-1, 0))
                else:
                    if self.get_tile(x - 1, y).walkable:
                        directions.append((-1, 0))
                    if self.get_tile(x + 1, y).walkable:
                        directions.append((1, 0))
                    if self.get_tile(x, y - 1).walkable:
                        directions.append((0, -1))
                    if self.get_tile(x, y + 1).walkable:
                        directions.append((0, 1))
                neighbors[x][y] = directions
        return neighbors

    def get_tile(self, x, y):
        return self.tiles[x % self.width][y % self.height]

    def get_directions(self, x, y):
        if (x + y) & 1 == 0:
            return [(0, 1, 'N'), (0, -1, 'S'), (1, 0, 'E'), (-1, 0, 'W')]
        return [(-1, 0, 'W'), (1, 0, 'E'), (0, -1, 'S'), (0, 1, 'N')]

    def breadth_search(self, start, target_func, max_distance=0, get_all_options=False):
        cell = self.get_tile(start.x, start.y)
        if target_func(cell, Position(start.x, start.y)):
            return None

        frontier = Queue()
        frontier.enqueue((start.x, start.y))

        path_from = {(start.x, start.y): (0, 0)}

        while not frontier.empty():
            current = frontier.dequeue()

            if target_func(self.get_tile(current[0], current[1]), Position(current[0], current[1])):
                path = ''
                current_position = current
                next_movement = path_from[current_position]
                while next_movement != (0, 0):
                    if next_movement == (0, 1):
                        path = 'N' + path
                    if next_movement == (0, -1):
                        path = 'S' + path
                    if next_movement == (1, 0):
                        path = 'E' + path
                    if next_movement == (-1, 0):
                        path = 'W' + path
                    current_position = ((current_position[0] - next_movement[0] + self.width) % self.width,
                                        (current_position[1] - next_movement[1] + self.height) % self.height)
                    next_movement = path_from[current_position]

                return MovePosition(current[0], current[1], path)

            for dir in self.neighbors[current[0]][current[1]]:
                new_pos = ((current[0] + dir[0] + self.width) % self.width, (current[1] + dir[1] + self.height) % self.height)
                if new_pos not in path_from:
                    path_from[new_pos] = (dir[0], dir[1])
                    frontier.enqueue(new_pos)
        return None

    def heuristic(self, a, b):
        x = abs(a.x - b.x)
        if x > self.half_width:
            x = self.width - x
        y = abs(a.y - b.y)
        if y > self.half_height:
            y = self.height - y
        return x + y

    def depth_search(self, start, target, max_distance=0):
        frontier = PriorityQueue()
        frontier.enqueue(MoveCostPosition(start.x, start.y, '', 0))
        cost_at = {(start.x, start.y): 0}

        while not frontier.empty():
            current = frontier.dequeue()

            if current.x == target.x and current.y == target.y:
                return MovePosition(current.x, current.y, current.direction)

            for dir in self.get_directions(current.x, current.y):
                new_cost = cost_at[(current.x, current.y)] + 1
                next_pos = MoveCostPosition((current.x + dir[0] + self.width) % self.width,
                                            (current.y + dir[1] + self.height) % self.height,
                                            current.direction + dir[2], 0)
                pos_tuple = (next_pos.x, next_pos.y)

                if self.get_tile(next_pos.x, next_pos.y).walkable and (pos_tuple not in cost_at or new_cost < cost_at[pos_tuple]):
                    cost_at[pos_tuple] = new_cost
                    next_pos.priority = new_cost + self.heuristic(target, next_pos)
                    frontier.enqueue(next_pos)
        return None

    def copy(self):
        new_world = World(self.width, self.height, self.tiles.copy())
        new_world.neighbors = new_world.generate_neighbors()
        return new_world
    
    
    