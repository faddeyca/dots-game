import pygame
import sys

from colors import *


moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]


class Game:
    def __init__(self):
        self.up_length = 100
        self.linesX = 20
        self.linesY = 20
        self.block_size = 25
        self.up_length = 100
        self.gap = 50
        self.size = [self.block_size * (self.linesX - 1) + self.gap * 2,
                     self.up_length + self.block_size * (self.linesY - 1) + 2 * self.gap]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()

        self.turn = 0
        self.table =  [[-1] * self.linesY for i in range(self.linesX)]
        self.components_counter = [0, 0]
        self.used = []

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

        for x in range(self.linesX):
            for y in range(self.linesY):
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

    def get_neighbours(self, pos):
        x = pos[0]
        y = pos[1]
        current = self.table[x][y] % 2
        enemy = (current + 1) % 2
        res = []
        for ax, ay in moves4:
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if self.table[nx][ny] < 0:
                continue
            if self.table[nx][ny] % 2 != current:
                continue
            res.append((nx, ny))
        for ax, ay in moves4x:
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if self.table[nx][ny] < 0:
                continue
            if self.table[nx][ny] % 2 != current:
                continue
            dx = nx - x
            dy = ny - y
            if self.table[x + dx][y] >= 0 and self.table[x][y + dy] >= 0:
                first = self.table[x + dx][y] % 2 == enemy
                second = self.table[x][y + dy] % 2 == enemy
                if first and second:
                    continue
            res.append((nx, ny))
        return res

    def fill_component(self, pos, val):
        x = pos[0]
        y = pos[1]
        self.table[x][y] = val
        dots = self.get_neighbours(pos)
        for dot in dots:
            if self.table[dot[0]][dot[1]] != val:
                self.fill_component(dot, val)

    def get_next_component_value(self, current):
        ans = self.components_counter[current] * 2 + current
        self.components_counter[current] += 1
        return ans

    def refill_components(self, current):
        amount = self.components_counter[current]
        for i in range(amount):
            old = i * 2 + current
            flag = False
            for x in range(self.linesX):
                if flag:
                    break
                for y in range(self.linesY):
                    if self.table[x][y] == old:
                        new = self.get_next_component_value(current)
                        self.fill_component((x, y), new)
                        flag = True
                        break

    def check(self, current):
        enemy = (current + 1) % 2
        component = []
        left = self.linesX
        right = 0
        up = self.linesY
        down = 0
        for x in range(self.linesX):
            for y in range(self.linesY):
                if self.table[x][y] == current:
                    component.append((x, y))
                    left = min(left, x)
                    right = max(right, x)
                    up = min(up, y)
                    down = max(down, y)
        left -= 1
        right += 1
        up -= 1
        down += 1
        if left < 0 or right >= self.linesX or up < 0 or down >= self.linesY:
            return

        for x in range(left, right + 1):
            angry = False
            for y in range(up, down + 1):
                if self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] == current:
                    if not angry:
                        return
                elif self.table[x][y] % 2 == enemy:
                    angry = True
        
        for x in range(left, right + 1):
            angry = False
            for y in reversed(range(up, down + 1)):
                if self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] == current:
                    if not angry:
                        return
                elif self.table[x][y] % 2 == enemy:
                    angry = True

        for y in range(up, down + 1):
            angry = False
            for x in range(left, right + 1):
                if self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] == current:
                    if not angry:
                        return
                elif self.table[x][y] % 2 == enemy:
                    angry = True
        
        for y in range(up, down + 1):
            angry = False
            for x in reversed(range(left, right + 1)):
                if self.table[x][y] < 0:
                    angry = False
                elif self.table[x][y] == current:
                    if not angry:
                        return
                elif self.table[x][y] % 2 == enemy:
                    angry = True
        
        self.score[enemy] += len(component)
        for x, y in component:
            self.table[x][y] = -2

    def put_dot(self, pos):
        if pos in self.used:
            return

        self.table[pos[0]][pos[1]] = self.get_next_component_value(self.turn)

        self.refill_components(0)
        self.refill_components(1)

        for i in range(self.components_counter[0]):
            self.check(i * 2)

        for i in range(self.components_counter[1]):
            self.check(i * 2 + 1)

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
                    if event.button == 1:
                        self.put_dot(pos)

            self.draw_window()
            self.draw_text()
            self.draw_env()
            pygame.display.flip()
            self.timer.tick(60)


if __name__ == "__main__":
    game = Game()
    game.start()