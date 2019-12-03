from collections import deque
from collections import namedtuple
import heapq

Position = namedtuple('Position', ['x', 'y'])

class Tile:
    def __init__(self, walkable, hive=False, was_hive=False, hive_index=-1, food=False, bee=None):
        self.walkable = walkable
        self.hive = hive
        self.was_hive = hive or was_hive
        self.hive_index = hive_index
        self.food = food
        self.bee = bee
        self.food_level = -1


class Bot:
    def __init__(self, name, ai, colour):
        self.name = name
        self.terminated = False
        self.terminated_reason = ''
        self.lost = False
        self.points = 60
        self.food_collected = 0
        self.position = 1
        self.timeouts = 5
        self.ai = ai
        self.hive_colour = (max(colour[0] - 40, 0), max(colour[1] - 40, 0), max(colour[2] - 40, 0))
        self.colour = colour
        self.hives = []
        self.hive_positions = []
        self.bees = deque()

class Bee:
    def __init__(self, index, position, health=6, data='', action_success=True):
        self.index = index
        self.position = position
        self.health = health
        self.data = data
        self.action = ''
        self.action_success = action_success

    def copy(self):
        return Bee(self.index, self.position, self.health, self.data, self.action_success)

class MovePosition:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

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

    def enqueue(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def dequeue(self):
        return heapq.heappop(self.elements)

    def to_list(self):
        return [e[0] for e in self.elements]


class World:
    def __init__(self, width, height, tiles, neighbors=None):
        self.width = width
        self.half_width = int(width / 2)
        self.height = height
        self.half_height = int(height / 2)
        self.tiles = tiles
        self._neighbors = neighbors

    def copy(self):
        new_tiles = [[None for y in range(self.height)] for x in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                tile = self.get_tile(x, y)
                new_tiles[x][y] = Tile(tile.walkable, tile.hive, tile.was_hive, tile.hive_index, tile.food, None if tile.bee is None else tile.bee.copy())
        return World(self.width, self.height, new_tiles, self._neighbors.copy())

    def generate_neighbors(self):
        self._neighbors = [[[] for y in range(self.height)] for x in range(self.width)]
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
                self._neighbors[x][y] = directions

    def get_tile(self, x, y):
        return self.tiles[x % self.width][y % self.height]

    def get_x_in_range(self, start, target_func, max_distance, sort_func=None):
        """Returns a list of the positions of all locations that meet the target_func criteria"""
        if sort_func is None:
            targets = []
            for x in range(-max_distance, max_distance + 1):
                for y in range(-max_distance, max_distance + 1):
                    distance = abs(x) + abs(y)
                    if distance > max_distance:
                        continue
                    pos = Position(start.x + x, start.y + y)
                    if target_func(pos, distance):
                        targets.append(pos)
            return targets
        else:
            targets = PriorityQueue()
            for x in range(-max_distance, max_distance + 1):
                for y in range(-max_distance, max_distance + 1):
                    distance = abs(x) + abs(y)
                    if distance > max_distance:
                        continue
                    pos = Position(start.x + x, start.y + y)
                    if target_func(pos, distance):
                        targets.enqueue(sort_func(pos, distance), pos)
            return targets.to_list()

    def breadth_path(self, start, max_distance=5318008):
        frontier = Queue()
        path_from = {}
        path_dirs = {}

        if isinstance(start, list):
            for pos in start:
                frontier.enqueue((pos, 0))

                path_from[pos] = (0, 0)
                path_dirs[pos] = ''
        else:
            frontier.enqueue((start, 0))

            path_from[start] = (0, 0)
            path_dirs[start] = ''

        if max_distance <= 0:
            max_distance = 5318008

        while not frontier.empty():
            dequeued = frontier.dequeue()
            current = dequeued[0]

            cost = dequeued[1] + 1
            if cost <= max_distance:
                for dir in self._neighbors[current.x][current.y]:
                    new_pos = Position((current.x + dir[0] + self.width) % self.width, (current.y + dir[1] + self.height) % self.height)

                    if new_pos not in path_from:
                        path_from[new_pos] = (dir[0], dir[1])
                        if dir == (0, -1):
                            path_dirs[new_pos] = 'N'
                        if dir == (-1, 0):
                            path_dirs[new_pos] = 'E'
                        if dir == (0, 1):
                            path_dirs[new_pos] = 'S'
                        if dir == (1, 0):
                            path_dirs[new_pos] = 'W'
                        frontier.enqueue((new_pos, cost))

        return path_dirs

    def breadth_search(self, start, target_func, max_distance=5318008, get_all_options=False):
        frontier = Queue()
        frontier.enqueue(((start.x, start.y), 0))

        path_from = {(start.x, start.y): (0, 0)}
        returnable = [] if get_all_options else None

        if max_distance <= 0:
            max_distance = 5318008

        while not frontier.empty():
            dequeued = frontier.dequeue()
            current = dequeued[0]

            if target_func(Position(current[0], current[1]), dequeued[1]):
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
                                        (current_position[1] - next_movement[
                                            1] + self.height) % self.height)
                    next_movement = path_from[current_position]

                if get_all_options:
                    returnable.append(MovePosition(current[0], current[1], path))
                else:
                    return MovePosition(current[0], current[1], path)

            cost = dequeued[1] + 1
            if cost <= max_distance:
                for dir in self._neighbors[current[0]][current[1]]:
                    new_pos = ((current[0] + dir[0] + self.width) % self.width, (current[1] + dir[1] + self.height) % self.height)

                    if new_pos not in path_from:
                        path_from[new_pos] = (dir[0], dir[1])
                        frontier.enqueue((new_pos, cost))
        return returnable

    def manhattan(self, a, b_tuple):
        x = abs(a.x - b_tuple[0])
        if x > self.half_width:
            x = self.width - x
        y = abs(a.y - b_tuple[1])
        if y > self.half_height:
            y = self.height - y
        return x + y

    def depth_search(self, start, target, max_distance=5318008):
        frontier = PriorityQueue()
        frontier.enqueue((start.x, start.y), 0)

        cost_at = {(start.x, start.y): 0}
        path_from = {(start.x, start.y): (0, 0)}

        while not frontier.empty():
            current = frontier.dequeue()[1]

            if current[0] == target.x and current[1] == target.y:
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

            for dir in self._neighbors[current[0]][current[1]]:
                new_cost = cost_at[(current[0], current[1])] + 1
                if new_cost < max_distance:
                    next_pos = ((current[0] + dir[0] + self.width) % self.width, (current[1] + dir[1] + self.height) % self.height)

                    if self.get_tile(next_pos[0], next_pos[1]).walkable and (next_pos not in cost_at or new_cost < cost_at[next_pos]):
                        cost_at[next_pos] = new_cost
                        path_from[next_pos] = (dir[0], dir[1])
                        frontier.enqueue(next_pos, new_cost + self.manhattan(target, next_pos))
        return None
