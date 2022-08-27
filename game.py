from queue import Queue
import pygame
import sys
from functools import reduce
import operator
import math
from copy import deepcopy
from properties import Properties as p
from game_drawer import draw_env
from computer import Robot


class Game:
    def __init__(self, linesX, linesY,
                 mode,
                 player=0, names=("Синие", "Красные"),
                 computer=None):
        self.linesX = linesX
        self.linesY = linesY
        self.mode = mode
        self.player = player

        self.turn = 0
        self.dots = [[], [], [], [], []]
        self.polygons = []
        self.score = [0, 0]

        self.prev_turn = None
        self.prev_dots = None
        self.prev_polygons = None
        self.prev_score = None

        self.computer = computer
        self.names = names
        self.size = [p.block_size * (self.linesX - 1) + p.gap * 2,
                     p.up_length +
                     p.block_size * (self.linesY - 1) + 2 * p.gap]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()

    def get_neighbours(self, table, x, y):
        moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]
        res = []
        for ax, ay in moves4:
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if table[nx][ny] != -1:
                continue
            res.append((nx, ny))
        for ax, ay in moves4x:
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if table[nx][ny] != -1:
                continue
            dx = nx - x
            dy = ny - y
            first = table[x + dx][y] == 1
            second = table[x][y + dy] == 1
            if first and second:
                continue
            res.append((nx, ny))
        return res

    def bfs(self, table, x, y, val=0):
        q = Queue()
        q.put((x, y))
        count = 1
        while count > 0:
            x, y = q.get()
            count -= 1
            if table[x][y] == val:
                continue
            table[x][y] = val
            dots = self.get_neighbours(table, x, y)
            for dot in dots:
                q.put(dot)
                count += 1

    def build_cover(self, table, current):
        def get_count(x, y):
            dot = None
            count = 0
            if x - 1 >= 0 and table[x - 1][y] == 2:
                count += 1
            else:
                dot = (x - 1, y)
            if x + 1 < self.linesX and table[x + 1][y] == 2:
                count += 1
            else:
                dot = (x + 1, y)
            if y - 1 >= 0 and table[x][y - 1] == 2:
                count += 1
            else:
                dot = (x, y - 1)
            if y + 1 < self.linesY and table[x][y + 1] == 2:
                count += 1
            else:
                dot = (x, y + 1)
            return count, dot

        p = []
        for x in range(self.linesX):
            for y in range(self.linesY):
                if table[x][y] == 1:
                    count, dot = get_count(x, y)
                    if count == 3:
                        if get_count(dot[0], dot[1])[0] == 0:
                            p.append((x, y))
                    elif count > 0 and count != 4:
                        p.append((x, y))
                if table[x][y] == 2:
                    self.dots[4].append((x, y))

        if len(p) != 0:
            center = tuple(
                           map(
                               operator.truediv,
                               reduce
                               (lambda x, y: map
                                (operator.add, x, y), p), [len(p)] * 2))
            p = sorted(p,
                       key=lambda coord:
                       (-135 - math.degrees
                        (math.atan2(
                         *tuple
                         (map(operator.sub,
                          coord, center))[::-1]))) % 360)
            self.polygons.append((p, current))

    def check(self, current):
        table = []
        for x in range(self.linesX):
            line = []
            for y in range(self.linesY):
                if (x, y) in self.dots[current]:
                    line.append(1)
                else:
                    line.append(-1)
            table.append(line)

        for x in range(self.linesX):
            if table[x][0] == -1:
                self.bfs(table, x, 0)
        for x in range(self.linesX):
            if table[x][self.linesY - 1] == -1:
                self.bfs(table, x, self.linesY - 1)
        for y in range(self.linesY):
            if table[0][y] == -1:
                self.bfs(table, 0, y)
        for y in range(self.linesY):
            if table[self.linesX - 1][y] == -1:
                self.bfs(table, self.linesX - 1, y)

        to_fill = []
        enemy = (current + 1) % 2
        for x in range(self.linesX):
            for y in range(self.linesY):
                if table[x][y] == -1:
                    if (x, y) in self.dots[current + 2]:
                        self.dots[current + 2].remove((x, y))
                        self.dots[current].append((x, y))
                        self.score[enemy] -= 1
                    if (x, y) in self.dots[enemy]:
                        to_fill.append((x, y))
                        self.dots[enemy].remove((x, y))
                        self.dots[enemy + 2].append((x, y))
                        self.score[current] += 1
        for x, y in to_fill:
            self.bfs(table, x, y, 2)

        self.build_cover(table, current)

    def is_avilable(self, pos):
        a = pos in self.dots[0]
        b = pos in self.dots[1]
        c = pos in self.dots[2]
        d = pos in self.dots[3]
        e = pos in self.dots[4]
        return not (a or b or c or d or e)

    def save_prev(self):
        self.prev_turn = self.turn
        self.prev_dots = deepcopy(self.dots)
        self.prev_polygons = self.polygons.copy()
        self.prev_score = self.score.copy()

    def load_prev(self):
        if self.prev_dots is None:
            return
        self.turn = self.prev_turn
        self.dots = self.prev_dots
        self.polygons = self.prev_polygons
        self.score = self.prev_score

    def put_dot(self, pos, lock=False):
        if not lock:
            self.save_prev()

        self.dots[self.turn].append(pos)

        self.check(self.turn)
        self.check((self.turn + 1) % 2)

        if self.mode != 2:
            self.turn += 1
            self.turn %= 2

    def get_mouse_pos(self, pos):
        x = (pos[0] - p.gap) / p.block_size
        y = (pos[1] - p.gap - p.up_length) / p.block_size
        delta = 0.3
        a = x % 1 <= delta or x % 1 >= (1 - delta)
        b = y % 1 <= delta or y % 1 >= (1 - delta)
        if not (a and b):
            return -1
        x = round(x)
        y = round(y)
        if x < 0 or x >= self.linesX or y < 0 or y >= self.linesY:
            return -1
        return x, y

    def start(self):
        pygame.init()
        pos = -1
        amount = self.linesX * self.linesY
        if self.mode == 1:
            if self.player == 1:
                self.put_dot((self.linesX // 2, self.linesY // 2), lock=True)
        while 1:
            count = (len(self.dots[0]) +
                     len(self.dots[1]) +
                     len(self.dots[4]))
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if count == amount:
                    return self.score
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return self.score
                    if event.key == pygame.K_r:
                        self.load_prev()
                pos = self.get_mouse_pos(pygame.mouse.get_pos())
                if not self.is_avilable(pos):
                    pos = -1
                if event.type == pygame.MOUSEBUTTONUP:
                    if pos == -1:
                        continue
                    if self.mode == 0:
                        if event.button == 1:
                            self.put_dot(pos)
                    if self.mode == 1:
                        if event.button == 1:
                            self.put_dot(pos)
                            rpos = self.computer.move(pos)
                            if rpos != -1:
                                self.put_dot(rpos, True)
                    if self.mode == 2:
                        if event.button == 1:
                            self.turn = 0
                            self.put_dot(pos)
                        if event.button == 2:
                            self.load_prev()
                        if event.button == 3:
                            self.turn = 1
                            self.put_dot(pos)

            self.timer.tick(60)
            draw_env(self.screen, self.size, pos,
                     self.linesX, self.linesY, self.mode,
                     self.turn,
                     self.dots, self.polygons,
                     self.score,
                     self.names)
            pygame.display.flip()
