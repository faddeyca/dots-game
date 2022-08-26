from math import atan2, pi
from queue import Queue
import pygame
import sys

from colors import *


moves8 = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]


class Game:
    def __init__(self, linesX, linesY, mode):
        self.linesX = linesX
        self.linesY = linesY
        self.mode = mode

        self.block_size = 25
        self.up_length = 100
        self.gap = 50
        self.size = [self.block_size * (self.linesX - 1) + self.gap * 2,
                     self.up_length + self.block_size * (self.linesY - 1) + 2 * self.gap]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()

        self.turn = 0
        self.table =  ([[-1] * self.linesY for i in range(self.linesX)],
                       [[-1] * self.linesY for i in range(self.linesX)])
        self.used = []
        self.dots = [[], [], []]
        self.polygons = []
        self.score = [0, 0]

    def draw_window(self):
        self.screen.fill(Color.white)
        pygame.draw.rect(self.screen, Color.up_menu,
                            [0, 0, self.size[0], self.up_length])

    def draw_env(self):
        for column in range(self.linesX):
            self.draw_vertical_line(Color.black, column)
        for row in range(self.linesY):
            self.draw_horizontal_line(Color.black, row)

        for dot in self.dots[0]:
            self.draw_dot(Color.red, dot[0], dot[1])
        for dot in self.dots[1]:
            self.draw_dot(Color.blue, dot[0], dot[1])
        for dot in self.dots[2]:
            self.draw_dot(Color.green, dot[0], dot[1])

        for polygon in self.polygons:
            self.draw_polygon(polygon)

    def draw_polygon(self, polygon):
        npolygon = []
        for dot in polygon:
            x = self.gap + dot[0] * self.block_size
            y = self.gap + dot[1] * self.block_size + self.up_length
            npolygon.append((x, y))
        pygame.draw.polygon(self.screen, Color.green, npolygon)

    def draw_dot(self, color, x, y):
        xc = self.gap + x * self.block_size
        yc = self.up_length + self.gap + y * self.block_size
        pygame.draw.circle(self.screen, color, [xc, yc], 4)

    def draw_vertical_line(self, color, column):
        xb = self.gap + column * self.block_size
        yb = self.gap + self.up_length
        xe = self.gap + column * self.block_size
        ye = self.gap + self.block_size * (self.linesY - 1) + self.up_length
        pygame.draw.line(self.screen, color, [xb, yb], [xe, ye])

    def draw_horizontal_line(self, color, row):
        xb = self.gap
        yb = self.gap + self.up_length + row * self.block_size
        xe = self.gap + (self.linesX - 1) * self.block_size
        ye = self.gap + self.up_length + row * self.block_size
        pygame.draw.line(self.screen, color, [xb, yb], [xe, ye])

    def draw_text(self):
        k = self.linesX / 20
        courier = pygame.font.SysFont('courier', int(35 * k))
        text_score_1 = courier.render(f"Score 1: {self.score[0]}", 0, Color.white)
        self.screen.blit(text_score_1, (20, 20))
        text_score_2 = courier.render(f"Score 2: {self.score[1]}", 0, Color.white)
        self.screen.blit(text_score_2, (300, 20))

    def get_neighbours(self, table, x, y):
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

    def bfs(self, table, x, y):
        q = Queue()
        q.put((x, y))
        count = 1
        while count > 0:
            x, y = q.get()
            count -= 1
            if table[x][y] == 0:
                continue
            table[x][y] = 0
            dots = self.get_neighbours(table, x, y)
            for dot in dots:
                q.put(dot)
                count += 1

    def check(self, current):
        table = []
        for x in range(self.linesX):
            line = []
            for y in range(self.linesY):
                line.append(self.table[current][x][y])
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
        
        enemy = (current + 1) % 2
        for x in range(self.linesX):
            for y in range(self.linesY):
                if self.table[enemy][x][y] == 1 and table[x][y] == -1:
                    self.dots[2].append((x, y))
                    self.table[enemy][x][y] = -1
                    self.score[current] += 1

    def put_dot(self, pos):
        if pos in self.used:
            return
        self.used.append(pos)
        self.dots[self.turn].append(pos)
        self.table[self.turn][pos[0]][pos[1]] = 1
        
        self.check(0)
        self.check(1)

        if self.mode == 0:
            self.turn += 1
            self.turn %= 2

    def get_mouse_pos(self, pos):
        x = (pos[0] - self.gap) / self.block_size
        y = (pos[1] - (self.gap + self.up_length)) / self.block_size
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
            self.draw_window()
            self.draw_text()
            self.draw_env()
            pygame.display.flip()


if __name__ == "__main__":
    game = Game(20, 20, 2)
    game.start()