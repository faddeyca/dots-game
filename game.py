from queue import Queue
import pygame
import sys
from functools import reduce
import operator
import math

from properties import Properties as p
from drawer import draw_env


class Game:
    def __init__(self, linesX, linesY, mode):
        self.linesX = linesX
        self.linesY = linesY
        self.mode = mode

        self.turn = 0
        self.dots = [[], [], [], [], []]
        self.polygons = []
        self.score = [0, 0]

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
                if (x, y) in self.dots[enemy] and table[x][y] == -1:
                    to_fill.append((x, y))
                    self.dots[enemy].remove((x, y))
                    self.dots[enemy + 2].append((x, y))
                    self.score[current] += 1
        for x, y in to_fill:
            self.bfs(table, x, y, 2)
        p = []
        dot = None
        for x in range(self.linesX):
            for y in range(self.linesY):
                if table[x][y] == 2:
                    self.dots[4].append((x, y))
                    if table[x - 1][y] == 1:
                        p.append([x - 1, y])
                    if table[x + 1][y] == 1:
                        p.append([x + 1, y])
                    if table[x][y - 1] == 1:
                        p.append([x, y - 1])
                    if table[x][y + 1] == 1:
                        p.append([x, y + 1])

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

    def put_dot(self, pos):
        a = pos in self.dots[0]
        b = pos in self.dots[1]
        c = pos in self.dots[2]
        d = pos in self.dots[3]
        e = pos in self.dots[4]
        if a or b or c or d or e:
            return
        self.dots[self.turn].append(pos)

        self.check(0)
        self.check(1)

        if self.mode == 0:
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
        if x < 0 or x > self.linesX or y < 0 or y > self.linesY:
            return -1
        return x, y

    def start(self):
        pygame.init()
        while 1:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = self.get_mouse_pos(pygame.mouse.get_pos())
                    if pos == -1:
                            continue
                    if self.mode == 0:
                        if event.button == 1:
                            self.put_dot(pos)
                    if self.mode == 2:
                        if event.button == 1:
                            self.turn = 0
                            self.put_dot(pos)
                        if event.button == 3:
                            self.turn = 1
                            self.put_dot(pos)

            self.timer.tick(60)
            draw_env(self.screen, self.size,
                     self.linesX, self.linesY, self.mode,
                     self.dots, self.polygons,
                     self.score)
            pygame.display.flip()


if __name__ == "__main__":
    game = Game(20, 20, 2)
    game.start()
