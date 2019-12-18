# Here are all the important values you may want to change for testing purposes
X_GRIDS = 3
Y_GRIDS = 3

MAX_TURNS = 750
TIMEOUT = 0.5

# All the imports used in this program
import _thread
import importlib
import math
import traceback
import random
import sys
import threading
from contextlib import contextmanager
from os import listdir
from os.path import isfile, join

import pygame
from class_data import *

# Points are only used if the game lasts more than 1000 turns
# Here is how points work:
# Points are calculated by this formula:
# Points = 60 + destroyed_hives * 20 - hives_lost * 30 + turns_survived / 10 + total_food_collect / 4
#           automatic 0 if eliminated

# The rest of the constants being setup
BG = (171, 154, 138)
DEAD = (151, 134, 118)
BOARD = (191, 174, 158)
FOOD = (207, 230, 140)
WALL = (15, 15, 15)
BLACK = (0, 0, 0)
WAS_BLACK = (140, 130, 120)

X_SIZE = 32
Y_SIZE = 32

HIVE_COUNT = 2
BEE_RANGE = 3

X_GRID_SIZE = X_SIZE
Y_GRID_SIZE = Y_SIZE


class TimeoutException(Exception): pass


@contextmanager
def timeout_limit(seconds=TIMEOUT):
    # starts a thread to track the time, when the time is up it cancels the main thread with a Timeout exception
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


# helper functions to sort the bot list when the game is over
def get_position(bot):
    return bot.position


def get_points(bot):
    return -bot.points


class Game:
    def __init__(self, w, h):
        self.world = World(w, h, create_grid(w, h))
        self.bots = get_bots()
        self.world.tiles = self.set_hives(w, h, self.world.tiles)
        self.world.generate_neighbors()
        self.resize_board(math.floor(700 * max(X_SIZE / Y_SIZE, 1)) + 450, math.floor(700 * max(Y_SIZE / X_SIZE, 1)))

        self.turn = 0
        self.death_position = len(self.bots)
        self.game_ended = False
        self.rankings = None
        # uses deque instead of lists because they are slightly faster for a slightly larger memory penalty
        self.food_changes = deque()
        self.bee_changes = deque()
        self.eliminated_changes = deque()

        for _ in range(2):
            self.place_food()

        for bot in self.bots:
            # gives a copy of the world to each bot
            bot.ai.world = self.world.copy()

    def resize_board(self, w, h):
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.screen.set_alpha(None)
        self.cell_size = h / Y_SIZE
        self.half_cell = self.cell_size / 2
        self.x_plus = (w - (self.cell_size * X_SIZE))

    def render(self):
        self.screen.fill(BG)

        pygame.draw.rect(self.screen, WALL, (self.x_plus, 0, X_SIZE * self.cell_size, Y_SIZE * self.cell_size))

        hives = []
        was_hives = []
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                tile = self.world.get_tile(x, y)
                if tile.walkable:
                    if tile.hive:
                        if tile.hive_index == -1:
                            tile.hive = False
                            pygame.draw.rect(self.screen, BOARD,
                                             (x * self.cell_size + self.x_plus,
                                              (Y_SIZE - 1) * self.cell_size - y * self.cell_size,
                                              self.cell_size + 1, self.cell_size + 1))
                        else:
                            hives.append([x, y, self.bots[tile.hive_index].hive_colour])
                    elif tile.was_hive:
                        was_hives.append([x, y])
                    else:
                        pygame.draw.rect(self.screen, FOOD if tile.food else BOARD,
                                         (x * self.cell_size + self.x_plus,
                                          (Y_SIZE - 1) * self.cell_size - y * self.cell_size,
                                          self.cell_size + 1, self.cell_size + 1))
        for hive in hives:
            pygame.draw.rect(self.screen, BLACK,
                             (hive[0] * self.cell_size + self.x_plus - 2,
                              (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size - 2,
                              self.cell_size + 5, self.cell_size + 5))
            pygame.draw.rect(self.screen, hive[2],
                             (hive[0] * self.cell_size + self.x_plus,
                              (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size,
                              self.cell_size + 1, self.cell_size + 1))

        for hive in was_hives:
            pygame.draw.rect(self.screen, WAS_BLACK,
                             (hive[0] * self.cell_size + self.x_plus - 1,
                              (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size - 1,
                              self.cell_size + 3, self.cell_size + 3))
            pygame.draw.rect(self.screen, BOARD,
                             (hive[0] * self.cell_size + self.x_plus,
                              (Y_SIZE - 1) * self.cell_size - hive[1] * self.cell_size,
                              self.cell_size + 1, self.cell_size + 1))

        i = 0
        while i < len(self.bots):
            if not self.bots[i].terminated and not self.bots[i].lost:
                for bee in self.bots[i].bees:
                    pygame.draw.polygon(self.screen, self.bots[i].colour,
                                        [(bee.position.x * self.cell_size + self.x_plus + 1,
                                          (
                                                  Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.half_cell),
                                         (bee.position.x * self.cell_size + self.x_plus + self.half_cell,
                                          (Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + 1),
                                         (bee.position.x * self.cell_size + self.x_plus + self.cell_size - 1,
                                          (
                                                  Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.half_cell),
                                         (bee.position.x * self.cell_size + self.x_plus + self.half_cell,
                                          (
                                                  Y_SIZE - 1) * self.cell_size - bee.position.y * self.cell_size + self.cell_size - 1)])

            i = i + 1

    def render_text(self):
        big_font = pygame.font.SysFont('microsoftsansserif', 24)
        font = pygame.font.SysFont('microsoftsansserif', 18)

        if self.game_ended:
            text = big_font.render(''.join(['Turn: ', str(self.turn), '      | Game Ended |']), True, BLACK, None)
        else:
            text = big_font.render(''.join(['Turn: ', str(self.turn)]), True, BLACK, None)
        text_rect = text.get_rect()
        text_rect.topleft = (5, 5)

        self.screen.blit(text, text_rect)

        i = 0
        height = 50
        while i < len(self.bots):
            killed = self.bots[i].lost or self.bots[i].terminated

            pygame.draw.rect(self.screen, DEAD if killed else self.bots[i].colour,
                             (10, 5 + height, self.x_plus - 20, 2 if killed else 8))

            big_font.set_bold(True)
            text = big_font.render(self.bots[i].team + ' | ', True, DEAD if killed else self.bots[i].colour, None)
            text_rect = text.get_rect()
            text_rect.topleft = (5, 15 + height)
            big_font.set_bold(False)

            self.screen.blit(text, text_rect)

            text = big_font.render(''.join([self.bots[i].name, ': ',
                                            ''.join(['TERMINATED [', self.bots[i].terminated_reason, ']']) if self.bots[
                                                i].terminated else ('DEAD' if self.bots[i].lost else 'Active')]), True,
                                   DEAD if killed else self.bots[i].colour, None)
            text_rect_two = text.get_rect()
            text_rect_two.topleft = (text_rect.width + 5, 15 + height)

            self.screen.blit(text, text_rect_two)

            text = big_font.render(''.join([str(self.bots[i].points), ' | ', str(self.bots[i].position),
                                            get_position_suffix(self.bots[i].position)]), True,
                                   DEAD if killed else self.bots[i].colour, None)
            text_rect = text.get_rect()
            text_rect.topright = (self.x_plus - 5, 15 + height)

            self.screen.blit(text, text_rect)
            if killed:
                height = height + 55
            else:
                text = font.render(''.join(['Bees: ', str(len(self.bots[i].bees))]), True, self.bots[i].colour, None)
                text_rect = text.get_rect()
                text_rect.topleft = (5, 45 + height)

                self.screen.blit(text, text_rect)

                if self.bots[i].timeouts != 5:
                    text = font.render(''.join(['Time outs: ', str(5 - self.bots[i].timeouts)]), True,
                                       self.bots[i].colour, None)
                    text_rect = text.get_rect()
                    text_rect.topright = (self.x_plus - 5, 45 + height)

                    self.screen.blit(text, text_rect)

                height = height + 85

            i = i + 1

    def render_winner(self):
        font = pygame.font.SysFont('microsoftsansserif', 28)

        height = pygame.display.get_surface().get_size()[1]

        if self.rankings is None:
            self.rankings = self.bots.copy()
            if self.turn == MAX_TURNS:
                self.rankings.sort(key=get_points)
            else:
                self.rankings.sort(key=get_position)
            self.rankings = self.rankings[min(2, len(self.rankings) - 1)::-1]
            try:
                import pyperclip
                query = ""
                if len(self.rankings) == 3:
                    query = "UPDATE teams SET score=score+200, bsb1=bsb1+1 WHERE teamname='" + self.rankings[2].team + "';"
                if len(self.rankings) >= 2:
                    query += "UPDATE teams SET score=score+125, bsb2=bsb2+1 WHERE teamname='" + self.rankings[1].team + "';"
                if len(self.rankings) >= 1:
                    query += "UPDATE teams SET score=score+50, bsb3=bsb3+1 WHERE teamname='" + self.rankings[0].team + "';"
                pyperclip.copy(query)
            except: 
                pass

        position = len(self.rankings)
        for bot in self.rankings:
            font.set_bold(True)
            text = font.render(''.join([str(position), ': ', bot.team, ' | ']), True, bot.colour, None)
            text_rect = text.get_rect()
            text_rect.bottomleft = (5, height - 10)
            font.set_bold(False)

            self.screen.blit(text, text_rect)

            text = font.render(''.join([bot.name, ' | ', str(bot.points)]), True, bot.colour, None)
            text_rect_two = text.get_rect()
            text_rect_two.bottomleft = (text_rect.width + 5, height - 10)

            self.screen.blit(text, text_rect_two)

            position -= 1
            height -= 40

        text = font.render('WINNERS:', True, BLACK, None)
        text_rect = text.get_rect()
        text_rect.bottomleft = (10, height - 10)

        self.screen.blit(text, text_rect)

    def do_bee_attack(self, bee):
        if len(bee.action) >= 3 and bee.action[0] == 'A':
            bee.action = bee.action[2:]
            split = bee.action.split(',')
            x = int(split[0])
            y = int(split[1])
            bee.action = ''

            if self.world.manhattan(bee.position, (x, y)) <= BEE_RANGE:
                tile = self.world.get_tile(x, y)
                if tile.bee:
                    tile.bee.health = tile.bee.health - 1
                    self.bee_changes.append((tile.bee.copy(), x, y))
                    bee.action_success = True
                if tile.food:
                    tile.food = False
                    self.food_changes.append((False, x, y))

    def do_bee_movement(self, bee, direction, other_bee):
        # return 0 = false, 1 = true, 2 = deleted
        if len(bee.action) >= 3 and bee.action[0] == 'M':
            x = get_dir_x(bee.action[2])
            y = get_dir_y(bee.action[2])
            bee.action = ''
            if x == 0 and y == 0:
                return 0

            tile = self.world.get_tile(bee.position.x + x, bee.position.y + y)
            if tile.walkable:
                move = False
                if tile.bee is None:
                    move = True
                else:
                    bee_action = self.do_bee_movement(tile.bee, (x, y), bee)
                    same_direction = (-x != direction[0] and -y != direction[1])
                    if bee_action == 2:
                        return 0
                    elif not same_direction and bee_action == 1:
                        move = True
                    elif other_bee is not None and same_direction and other_bee.index != bee.index:
                        # enemy bees are moving directly against each other or one cant move and the other moves into it
                        if bee.health <= other_bee.health:
                            self.bots[bee.index].bees.remove(bee)
                            self.bee_changes.append((None, bee.position.x, bee.position.y))
                            self.world.tiles[bee.position.x][bee.position.y].bee = None

                        if other_bee.health >= bee.health:
                            self.bots[other_bee.index].bees.remove(other_bee)
                            self.bee_changes.append((None, other_bee.position.x, other_bee.position.y))
                            self.world.tiles[other_bee.position.x][other_bee.position.y].bee = None
                        return 2
                    elif tile.bee is not None and bee_action == 0 and tile.bee.index != bee.index:
                        # enemy bees are moving directly against each other or one cant move and the other moves into it
                        if bee.health >= tile.bee.health:
                            self.bots[bee.index].bees.remove(bee)
                            self.bee_changes.append((None, bee.position.x, bee.position.y))
                            self.world.tiles[bee.position.x][bee.position.y].bee = None

                        if tile.bee.health >= bee.health:
                            self.bots[tile.bee.index].bees.remove(tile.bee)
                            self.bee_changes.append((None, tile.bee.position.x, tile.bee.position.y))
                            tile.bee = None
                        return 2

                if move:
                    self.world.tiles[bee.position.x][bee.position.y].bee = None
                    self.bee_changes.append((None, bee.position.x, bee.position.y))

                    bee.position = Position((bee.position.x + x) % X_SIZE, (bee.position.y + y) % Y_SIZE)
                    bee.action_success = True

                    tile = self.world.tiles[bee.position.x][bee.position.y]
                    if tile.hive and tile.hive_index != bee.index:
                        i = 0
                        while i < len(self.bots[tile.hive_index].hives):
                            if tile == self.bots[tile.hive_index].hives[i]:
                                break
                            i = i + 1

                        self.bots[bee.index].points += 20
                        self.bots[tile.hive_index].points -= 30
                        self.eliminated_changes.append(self.bots[tile.hive_index].hive_positions.pop(i))
                        self.bots[tile.hive_index].hives.pop(i)
                        tile.hive = False

                        if len(self.bots[tile.hive_index].hives) == 0:
                            print(''.join(['Turn ', str(self.turn), ': Bot index [', str(tile.hive_index), '] '
                                                                                                           '(',
                                           self.bots[tile.hive_index].name, ') lost all hives, they are eliminated.']))

                            for kill_bee in self.bots[tile.hive_index].bees:
                                self.bee_changes.append((None, kill_bee.position.x, kill_bee.position.y))
                                self.world.tiles[kill_bee.position.x][kill_bee.position.y].bee = None

                            self.bots[tile.hive_index].position = self.death_position
                            self.death_position -= 1
                            self.bots[tile.hive_index].bees = []
                            self.bots[tile.hive_index].lost = True

                        tile.hive_index = -1
                    self.world.tiles[bee.position.x][bee.position.y].bee = bee
                    self.bee_changes.append((bee.copy(), bee.position.x, bee.position.y))
                    return 1
        return 0

    def check_bee_food(self, bees):
        for bee in bees:
            # also resets action for each bee
            bee.action = ''
            if self.world.tiles[bee.position.x][bee.position.y].food:
                self.food_changes.append((False, bee.position.x, bee.position.y))
                self.world.tiles[bee.position.x][bee.position.y].food = False
                self.bots[bee.index].food_collected += 1
                if self.bots[bee.index].food_collected & 3 == 0:
                    self.bots[bee.index].points += 1
                for hive in self.bots[bee.index].hives:
                    hive.food_level = hive.food_level + round(HIVE_COUNT / len(self.bots[bee.index].hives))

    def get_enemy_list(self, index):
        enemies = []
        i = 0
        while i < len(self.bots):
            if i != index and not self.bots[i].terminated and not self.bots[i].lost:
                enemies.append([i, self.bots[i].hive_positions.copy(), len(self.bots[i].bees)])
            i = i + 1
        return enemies

    def do_bots(self):
        # order of turn is:
        # 1. Spawn food
        # 2. Get bot action
        # 3. Attack
        # 4. Kill low health bots
        # 5. Move bots
        # 6. Collect food
        # 7. Destroy hives
        # 8. Spawn bees

        bot_length = len(self.bots)

        highest = max([len(bot.bees) for bot in self.bots])
        if highest < 80:
            if self.turn & 7 == 0:  # if turn % 8 == 0
                self.place_food()
        elif highest < 140:
            if self.turn & 15 == 0:  # if turn % 16 == 0
                self.place_food()
        elif highest < 200:
            if self.turn & 31 == 0:  # if turn % 32 == 0
                self.place_food()

        if self.turn % 5 == 0 and self.turn != 0:  # if turn % 32 == 0
            for bot in self.bots:
                if not bot.terminated and not bot.lost:
                    bot.points += 1

        i = 0
        terminated_bee_changes = []
        terminated_hive_changes = []
        any_terminations = False
        while i < bot_length:
            if not self.bots[i].terminated and not self.bots[i].lost:
                try:
                    with timeout_limit():
                        self.bots[i].ai.update_tiles(self.food_changes.copy(), self.bee_changes.copy(),
                                                     self.eliminated_changes.copy())
                        data_actions = self.bots[i].ai.do_turn([bee.copy() for bee in self.bots[i].bees],
                                                               self.get_enemy_list(i), self.turn)
                        for d_a, j in zip(data_actions, range(len(self.bots[i].bees))):
                            self.bots[i].bees[j].data = d_a[0]
                            self.bots[i].bees[j].action = d_a[1]
                except TimeoutException as e:
                    print(''.join(['Turn ', str(self.turn), ': Bot index [', str(i), '] (', self.bots[i].name,
                                   ') exceeded timelimit, no actions taken.']))
                    self.bots[i].timeouts -= 1
                    if self.bots[i].timeouts == 0:
                        print(''.join(['Turn ', str(self.turn), ': Bot index [', str(i), '] (', self.bots[i].name,
                                       ') timed out to many times. Terminating it.']))

                        any_terminations = True
                        self.bots[i].terminated = True
                        self.bots[i].terminated_reason = 'Timeout'
                        for bee in self.bots[i].bees:
                            terminated_bee_changes.append((None, bee.position.x, bee.position.y))
                            self.world.tiles[bee.position.x][bee.position.y].bee = None
                        self.bots[i].bees = []
                        for hive, pos in zip(self.bots[i].hives, self.bots[i].hive_positions):
                            terminated_hive_changes.append(pos)
                            hive.hive = False
                            hive.hive_index = -1
                        self.bots[i].hives = []
                        self.bots[i].points = 0

                        self.bots[i].position = self.death_position
                        self.death_position -= 1
                except Exception:
                    print(''.join(['Turn ', str(self.turn), ': Bot index [', str(i), '] (', self.bots[i].name,
                                   ') did a naughty. Terminating it.']))
                    print(" > Naughty details:", traceback.format_exc())

                    any_terminations = True
                    self.bots[i].terminated = True
                    self.bots[i].terminated_reason = 'Naughty'
                    for bee in self.bots[i].bees:
                        terminated_bee_changes.append((None, bee.position.x, bee.position.y))
                        self.world.tiles[bee.position.x][bee.position.y].bee = None
                    self.bots[i].bees = []
                    for hive, pos in zip(self.bots[i].hives, self.bots[i].hive_positions):
                        terminated_hive_changes.append(pos)
                        hive.hive = False
                        hive.hive_index = -1
                    self.bots[i].hives = []
                    self.bots[i].points = 0

                    self.bots[i].position = self.death_position
                    self.death_position -= 1
            i = i + 1

        while any_terminations:
            any_terminations = False
            i = 0
            while i < bot_length:
                if not self.bots[i].terminated and not self.bots[i].lost:
                    try:
                        with timeout_limit(TIMEOUT / 5):
                            self.bots[i].ai.update_tiles([].copy(), terminated_bee_changes.copy(),
                                                         terminated_hive_changes.copy())
                    except TimeoutException as e:
                        print(''.join(['Turn ', str(self.turn), '.5: Bot index [', str(i), '] (', self.bots[i].name,
                                       ') exceeded timelimit, no actions taken.']))
                    except Exception:
                        print(''.join(['Turn ', str(self.turn), '.5: Bot index [', str(i), '] (', self.bots[i].name,
                                       ') did a naughty. Terminating it.']))
                        print(" > Naughty details:", traceback.format_exc())

                        any_terminations = True
                        self.bots[i].terminated = True
                        self.bots[i].terminated_reason = 'Naughty'
                        for bee in self.bots[i].bees:
                            terminated_bee_changes.append((None, bee.position.x, bee.position.y))
                            self.world.tiles[bee.position.x][bee.position.y].bee = None
                        self.bots[i].bees = []
                        for hive, pos in zip(self.bots[i].hives, self.bots[i].hive_positions):
                            terminated_hive_changes.append(pos)
                            hive.hive = False
                            hive.hive_index = -1
                        self.bots[i].hives = []
                        self.bots[i].points = 0

                        self.bots[i].position = self.death_position
                        self.death_position -= 1
                i = i + 1

        self.food_changes = []
        self.bee_changes = []
        self.eliminated_changes = []

        for bot in self.bots:
            for bee in bot.bees:
                bee.action_success = False

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated and not self.bots[i].lost:
                for bee in self.bots[i].bees:
                    self.do_bee_attack(bee)
            i = i + 1

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated and not self.bots[i].lost:
                j = 0
                while j < len(self.bots[i].bees):
                    bee = self.bots[i].bees[j]
                    if bee.health <= 0:
                        self.world.tiles[bee.position.x][bee.position.y].bee = None
                        self.bee_changes.append((None, bee.position.x, bee.position.y))
                        del self.bots[i].bees[j]
                        j = j - 1
                    j = j + 1
            i = i + 1

        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                tile = self.world.get_tile(x, y)
                if tile.bee is not None:
                    self.do_bee_movement(tile.bee, (0, 0), None)

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated and not self.bots[i].lost:
                self.check_bee_food(self.bots[i].bees)  # check bee food also resets action
            i = i + 1

        i = 0
        while i < bot_length:
            if not self.bots[i].terminated and not self.bots[i].lost:
                j = 0
                while j < len(self.bots[i].hives):
                    hive = self.bots[i].hives[j]
                    if hive.food_level > 10:
                        hive.food_level = 10
                    if hive.bee is None and hive.food_level > 0:
                        hive.food_level = hive.food_level - 1
                        new_bee = Bee(i, Position(self.bots[i].hive_positions[j].x, self.bots[i].hive_positions[j].y))
                        self.bots[i].bees.append(new_bee)
                        self.world.tiles[new_bee.position.x][new_bee.position.y].bee = new_bee
                        self.bee_changes.append((new_bee.copy(), new_bee.position.x, new_bee.position.y))
                    j = j + 1
            i = i + 1

        self.turn = self.turn + 1

        active_bots = 0
        for bot in self.bots:
            if not bot.terminated and not bot.lost:
                active_bots = active_bots + 1
                if active_bots > 1:
                    break

        if self.turn >= MAX_TURNS or active_bots <= 1:
            self.game_ended = True

    def place_food(self):
        skips = random.randint(0, 20)
        x = random.randint(0, X_GRID_SIZE - 1)
        y = random.randint(0, Y_GRID_SIZE - 1)
        while 1:
            tile = self.world.get_tile(x, y)
            if tile.walkable and not tile.was_hive:
                if skips == 0:
                    break
                else:
                    skips = skips - 1
            x = x + 1
            if x >= X_GRID_SIZE:
                x = 0
                y = y + 1
                if y >= Y_GRID_SIZE:
                    y = 0

        for x_g in range(X_GRIDS):
            for y_g in range(Y_GRIDS):
                self.food_changes.append((True, x + x_g * X_GRID_SIZE, y + y_g * Y_GRID_SIZE))
                self.world.tiles[x + x_g * X_GRID_SIZE][y + y_g * Y_GRID_SIZE].food = True

    def set_hives(self, w, h, grid):
        i = 0  # index of bots
        for column in range(X_GRIDS):
            for row in range(Y_GRIDS):
                x_index = math.floor(w / X_GRIDS) * column
                y_index = math.floor(h / Y_GRIDS) * row

                for x in range(math.floor(w / X_GRIDS)):
                    for y in range(math.floor(h / Y_GRIDS)):
                        x_i = (x_index + x + w) % w
                        y_i = (y_index + y + h) % h
                        index = i if i < len(self.bots) else -1
                        if index == -1:
                            grid[x_i][y_i].hive = False
                        if grid[x_i][y_i].hive:
                            grid[x_i][y_i].hive_index = index
                            grid[x_i][y_i].food_level = 0

                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i)))
                            self.world.tiles[x_i][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i + 1, y_i)))
                            self.world.tiles[x_i + 1][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i + 1)))
                            self.world.tiles[x_i][y_i + 1].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i - 1, y_i)))
                            self.world.tiles[x_i - 1][y_i].bee = self.bots[i].bees[-1]
                            self.bots[i].bees.append(Bee(i, Position(x_i, y_i - 1)))
                            self.world.tiles[x_i][y_i - 1].bee = self.bots[i].bees[-1]
                            self.bots[grid[x_i][y_i].hive_index].hives.append(grid[x_i][y_i])
                            self.bots[grid[x_i][y_i].hive_index].hive_positions.append(Position(x_i, y_i))
                i = i + 1
        return grid

    def update(self):
        self.render()
        self.render_text()
        if not self.game_ended:
            self.do_bots()
        else:
            self.render_winner()


def get_position_suffix(pos):
    if pos == 1:
        return 'st'
    if pos == 2:
        return 'nd'
    if pos == 3:
        return 'rd'
    return 'th'


def get_dir_x(dir):
    if dir == 'E':
        return 1
    if dir == 'W':
        return -1
    return 0


def get_dir_y(dir):
    if dir == 'N':
        return 1
    if dir == 'S':
        return -1
    return 0


def create_grid(w, h):
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
    for column in range(X_GRIDS):
        for row in range(Y_GRIDS):
            x_index = math.floor(w / X_GRIDS) * column
            y_index = math.floor(h / Y_GRIDS) * row

            for x in range(math.floor(w / X_GRIDS)):
                for y in range(math.floor(h / Y_GRIDS)):
                    x_i = (x_index + x + w) % w
                    y_i = (y_index + y + h) % h
                    grid[x_i][y_i] = Tile(grid_part[x][y].walkable,
                                          grid_part[x][y].hive,
                                          grid_part[x][y].hive,
                                          -1)

    return grid


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
    # a list of all the possible colours of the bots
    colours = [(255, 180, 255), (0, 117, 220), (153, 63, 0), (50, 50, 60), (0, 92, 49), (0, 255, 0), (255, 255, 255),
               (128, 128, 128),
               (148, 255, 141), (113, 94, 0), (183, 224, 10), (194, 0, 136), (0, 51, 128), (203, 121, 5), (255, 0, 16),
               (112, 255, 255), (0, 153, 143), (255, 255, 0), (116, 10, 255), (90, 0, 0)]
    random.shuffle(colours)

    bot_path = './bots'

    # gets all the bots in the directory
    bot_names = [f[0:-3] for f in listdir(bot_path) if isfile(join(bot_path, f))]
    random.shuffle(bot_names)
    bots = []
    for i in range(len(bot_names)):
        try:
            clean = 1
            unclean_index = 0
            # scans the file for imports
            with open('bots/' + bot_names[i] + '.py', 'r') as f:
                while 1:
                    line = f.readline()
                    if not line:
                        break

                    line = line.partition('#')[0]
                    if not line.isspace():
                        line = line.strip()

                    unclean_index += 1
                    index = line.find('from ')
                    if index == 0:
                        if line[index + 5:] != 'class_data import *':
                            clean = 2
                            break
                    index = line.find('import')
                    if index == 0:
                        if not (line[index + 7:] == 'random' or line[index + 7:] == 'math' or line[
                                                                                              index + 7:] == 'itertools'):
                            clean = 2
                            break

                    if '(open(' in line or '=open(' in line or ' open(' in line:
                        clean = 3
                        break
                    index = max(line.find('\topen'), line.find('\nopen'), line.find(' open'), line.find('=open'),
                                line.find('(open'))
                    if index != -1:
                        index += 5
                        while index < len(line):
                            if line[index] == '(':
                                clean = 3
                                break
                            elif not line[index].isspace():
                                break
                            index = index + 1
                    if clean == 3:
                        break

                    if '__import__' in line:
                        clean = 2
                        break

            if clean == 1:
                bot_ai = importlib.import_module('bots.' + bot_names[i])
                # creates all the bots and appends it to the bot array
                bots.append(Bot(bot_names[i][:min(16, len(bot_names[i]))], bot_ai.TEAM, bot_ai.AI(i), colours.pop(0)))
                # each bot name is limited to only 16 characters
            else:
                if clean == 2:
                    print('Start: Bot (' + bot_names[i] + ') had illegal imports, it is not being included. Unclean line: ' + str(unclean_index))
                else:
                    print('Start: Bot (' + bot_names[i] + ') attempted to open a file, it is not being included. Unclean line: ' + str(unclean_index))
        except Exception:
            print('Start: Bot (' + bot_names[i] + ') did a naughty during creation. Not including it.')
            print(" > Naughty details:", traceback.format_exc())

    for i in range(len(bots)):
        print('Bot index [' + str(i) + '] is ' + str(bots[i].name))
    return bots


def get_winner():
    # used for getting the winners for the database
    if game is not None:
        if game.rankings is not None:
            return [game.rankings[len(game.rankings) - i - 1].team for i in range(len(game.rankings))]
    return None


def quit_game(force=False):
    if force:
        pygame.quit()
    else:
        sys.exit()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
game = None
X_SIZE *= X_GRIDS
Y_SIZE *= Y_GRIDS

pygame.init()
pygame.display.set_caption("CTF: Bee Swarm Battle")

# creates the game
game = Game(X_SIZE, Y_SIZE)

while 1:
    game.update()

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            game.resize_board(event.w, event.h)

