import pygame
import sys

from colors import *

moves8 = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]

class Game:
    def __init__(self):
        self.up_length = 100
        self.blocksX = 5
        self.blocksY = 5
        self.block_size = 25
        self.up_length = 100
        self.gap = 50
        self.turn = 0
        self.last = -1
        self.size = [self.block_size * self.blocksX + self.gap * 2,
                     self.up_length + self.block_size * self.blocksY + 2 * self.gap]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()
        self.table =  [[-1] * (self.blocksY + 1) for i in range(self.blocksX + 1)]
        self.comp = [0, 0]
        self.dots = [[], []]
        self.score = [0, 0]

    def draw_window(self):
        self.screen.fill(Color.white)
        pygame.draw.rect(self.screen, Color.up_menu,
                            [0, 0, self.size[0], self.up_length])

    def draw_env(self):
        for column in range(self.blocksX + 1):
            self.draw_vertical_line(Color.black, column)
        for row in range(self.blocksY + 1):
            self.draw_horizontal_line(Color.black, row)

        for x in range(self.blocksX + 1):
            for y in range(self.blocksY + 1):
                if self.table[x][y] == -2:
                    self.draw_dot(Color.green, x, y)
                elif self.table[x][y] != -1:
                    if self.table[x][y] % 2 == 0:
                        self.draw_dot(Color.red, x, y)
                    else:
                        self.draw_dot(Color.blue, x, y)

    def draw_dot(self, color, x, y):
        xc = self.gap + x * self.block_size
        yc = self.up_length + self.gap + y * self.block_size
        pygame.draw.circle(self.screen, color, [xc, yc], 4)

    def draw_vertical_line(self, color, column):
        xb = self.gap + column * self.block_size
        yb = self.gap + self.up_length
        xe = self.gap + column * self.block_size
        ye = self.gap + self.block_size * self.blocksY + self.up_length
        pygame.draw.line(self.screen, color, [xb, yb], [xe, ye])

    def draw_horizontal_line(self, color, row):
        xb = self.gap
        yb = self.gap + self.up_length + row * self.block_size
        xe = self.gap + self.blocksX * self.block_size
        ye = self.gap + self.up_length + row * self.block_size
        pygame.draw.line(self.screen, color, [xb, yb], [xe, ye])

    def draw_text(self):
        k = self.blocksX / 20
        courier = pygame.font.SysFont('courier', int(35 * k))
        text_score_1 = courier.render(f"Score 1: {self.score[0]}", 0, Color.white)
        self.screen.blit(text_score_1, (20, 20))
        text_score_2 = courier.render(f"Score 2: {self.score[1]}", 0, Color.white)
        self.screen.blit(text_score_2, (500, 20))

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
        if x < 0 or x > self.blocksX or y < 0 or y > self.blocksY:
            return -1
        return x, y

    def get_neighbours(self, pos):
        res = []
        for dx, dy in moves4:
            nx, ny = pos[0] + dx, pos[1] + dy
            if nx < 0 or nx >= self.blocksX or ny < 0 or ny >= self.blocksY:
                continue
            res.append((nx, ny))
        for dx, dy in moves4x:
            nx, ny = pos[0] + dx, pos[1] + dy
            if nx < 0 or nx >= self.blocksX or ny < 0 or ny >= self.blocksY:
                continue
            dx = nx - pos[0]
            dy = ny - pos[1]
            if self.table[pos[0] + dx][pos[1]] >= 0 and self.table[pos[0]][pos[1] + dy] >= 0:
                om = (self.table[pos[0]][pos[1]] + 1) % 2
                if self.table[pos[0] + dx][pos[1]] % 2 == om and self.table[pos[0]][pos[1] + dy] % 2 == om:
                    continue
            res.append((nx, ny))
        return res

    def recalculate_components(self):
        cur = self.comp[self.turn]
        for i in range(cur):
            c = i * 2 + self.turn
            flag = False
            for x in range(self.blocksX + 1):
                if flag:
                    break
                for y in range(self.blocksY + 1):
                    if self.table[x][y] == c:
                        a = self.comp[self.turn] * 2 + self.turn
                        self.fill_component(x, y, a, self.turn)
                        self.comp[self.turn] += 1
                        flag = True
                        break
            

        cur = self.comp[(self.turn + 1) % 2]
        for i in range(cur):
            c = i * 2 + (self.turn + 1) % 2
            flag = False
            for x in range(self.blocksX + 1):
                if flag:
                    break
                for y in range(self.blocksY + 1):
                    if self.table[x][y] == c:
                        a = self.comp[(self.turn + 1) % 2] * 2 + (self.turn + 1) % 2
                        self.fill_component(x, y, a, (self.turn + 1) % 2)
                        self.comp[(self.turn + 1) % 2] += 1
                        flag = True
                        break

    def fill_component(self, x, y, val, curr):
        self.table[x][y] = val
        neigh = self.get_neighbours((x, y))
        for nx, ny in neigh:
            if self.table[nx][ny] < 0:
                continue
            if self.table[nx][ny] == val:
                continue
            if self.table[nx][ny] % 2 == curr:
                self.fill_component(nx, ny, val, curr)

    def check(self, defence):
        attack = (defence + 1) % 2
        component = []
        left = self.blocksX
        right = 0
        up = self.blocksY
        down = 0
        for x in range(self.blocksX):
            for y in range(self.blocksY):
                if self.table[x][y] == defence:
                    component.append((x, y))
                    left = min(left, x)
                    right = max(right, x)
                    up = min(up, y)
                    down = max(down, y)

        left -= 1
        right += 1
        up -= 1
        down += 1
        
        flag = True
        for x in range(left, right + 1):
            angry = False
            for y in range(up, down + 1):
                if self.table[x][y] == defence:
                    if not angry:
                        flag = False
                    else:
                        break
                elif self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] % 2 == attack:
                    angry = True
        
        for x in range(left, right + 1):
            angry = False
            for y in reversed(range(up, down + 1)):
                if self.table[x][y] == defence:
                    if not angry:
                        flag = False
                    else:
                        break
                elif self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] % 2 == attack:
                    angry = True

        for y in range(up, down + 1):
            angry = False
            for x in range(left, right + 1):
                if self.table[x][y] == defence:
                    if not angry:
                        flag = False
                    else:
                        break
                elif self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] % 2 == attack:
                    angry = True
        
        for y in range(up, down + 1):
            angry = False
            for x in reversed(range(left, right + 1)):
                if self.table[x][y] == defence:
                    if not angry:
                        flag = False
                    else:
                        break
                elif self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] % 2 == attack:
                    angry = True

        if flag:
            self.score[attack] += len(component)
            for dot in component:
                self.table[dot[0]][dot[1]] = -2

    def put_dot(self, pos):
        if pos in self.dots[0] or pos in self.dots[1]:
            return

        self.dots[self.turn].append(pos)

        flag = True
        neigh = self.get_neighbours(pos)
        for nx, ny in neigh:
            if self.table[nx][ny] < 0:
                continue
            if self.table[nx][ny] % 2 == self.turn:
                flag = False
                self.fill_component(pos[0], pos[1], self.table[nx][ny], self.turn)

        if flag:
            a = self.comp[self.turn] * 2 + self.turn
            self.table[pos[0]][pos[1]] = a
            self.comp[self.turn] += 1

        self.recalculate_components()

        for i in range(self.comp[self.turn]):
            self.check(i * 2 + self.turn)

        for i in range(self.comp[(self.turn + 1) % 2]):
            self.check(i * 2 + (self.turn + 1) % 2)

        self.last = pos

        self.turn += 1
        self.turn %= 2


    def remove_dot(self, pos):
        if self.last == -1:
            return
        if self.last != pos:
            return

        if self.turn == 0:
            self.dots[1].pop()
            self.last = -1
            self.turn = 1
        else:
            self.dots[0].pop()
            self.last = -1
            self.turn = 0

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

                    if event.button == 1:
                        self.put_dot(pos)
                        
                    if event.button == 3:
                        self.remove_dot(pos)

            self.draw_window()
            self.draw_text()
            self.draw_env()
            pygame.display.flip()
            self.timer.tick(60)


if __name__ == "__main__":
    game = Game()
    game.start()