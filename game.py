from queue import Queue
import pygame
import sys

from properties import Properties as p
from drawer import draw_env


class Game:
    def __init__(self, linesX, linesY, mode):
        self.linesX = linesX
        self.linesY = linesY
        self.mode = mode

        self.turn = 0
        self.dots = [[], [], []]
        self.polygons = []
        self.score = [0, 0]

        self.size = [p.block_size * (self.linesX - 1) + p.gap * 2,
                     p.up_length + p.block_size * (self.linesY - 1) + 2 * p.gap]
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
        
        enemy = (current + 1) % 2
        for x in range(self.linesX):
            for y in range(self.linesY):
                if (x, y) in self.dots[enemy] and table[x][y] == -1:
                    self.dots[enemy].remove((x, y))
                    self.dots[2].append((x, y))
                    self.score[current] += 1

    def put_dot(self, pos):
        if pos in self.dots[0] or pos in self.dots[1] or pos in self.dots[2]:
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
    game = Game(20, 20, 0)
    game.start()
