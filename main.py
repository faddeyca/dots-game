from math import atan2, pi
import pygame
import sys

from colors import *


moves8 = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]


class Game:
    def __init__(self, linesX, linesY):
        self.linesX = linesX
        self.linesY = linesY

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
        self.components = dict()
        self.dots = [[], []]

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
        if val == -2:
            current = self.table[x][y] % 2
            if pos in self.dots[current]:
                self.dots[current].remove(pos)
        dots = self.get_neighbours(pos)
        self.table[x][y] = val
        for dot in dots:
            comp = self.table[dot[0]][dot[1]]
            if comp != val:
                self.fill_component(dot, val)

    def get_next_component_value(self, current):
        ans = self.components_counter[current] * 2 + current
        self.components_counter[current] += 1
        return ans

    def refill_components(self, components):
        for old in components:
            flag = False
            for x in range(self.linesX):
                if flag:
                    break
                for y in range(self.linesY):
                    if self.table[x][y] == old:
                        new = self.get_next_component_value(old % 2)
                        self.components[new] = (x, y)
                        self.fill_component((x, y), new)
                        flag = True
                        break
            flag = False
            for x in range(self.linesX):
                if flag:
                    break
                for y in range(self.linesY):
                    if self.table[x][y] == old:
                        flag = True
                        break
            if not flag:
                if old in self.components:
                    del self.components[old]

    def are_close(self, dot1, dot2):
        return abs(dot1[0] - dot2[0]) <= 1 and abs(dot1[1] - dot2[1]) <= 1

    def check_part_two(self, current):
        x, y = self.components[current]
        enemy = (current + 1) % 2
        angles = dict()
        min_dot = None
        min_dist = None
        for dot in self.dots[enemy]:
            angle = atan2(dot[0] - x, dot[1] - y)
            if angle not in angles:
                dist = ((dot[0] - x) ** 2 + (dot[1] - y) ** 2) ** 0.5
                angles[angle] = (dot, dist)
                if min_dot is None:
                    min_dot = angle
                    min_dist = dist
                else:
                    if dist < min_dist:
                        min_dist = dist
                        min_dot = angle
            else:
                dist = ((dot[0] - x) ** 2 + (dot[1] - y) ** 2) ** 0.5
                if dist < angles[angle][1]:
                    angles[angle] = (dot, dist)
                    if dist < min_dist:
                        min_dist = dist
                        min_dot = angle

        if min_dot is None:
            return -1
        ans1 = [angles[min_dot][0]]
        prev = min_dot
        prev_dot = angles[min_dot][0]
        for i in sorted(angles.keys()):
            if i > min_dot:
                if abs(prev - i) > pi / 2:
                    return -1
                dot = angles[i][0]
                if self.are_close(prev_dot, dot):
                    ans1.append(dot)
                    prev = i
                    prev_dot = dot
        ans2 = []
        prev = min_dot
        prev_dot = angles[min_dot][0]
        for i in reversed(sorted(angles.keys())):
            if i < min_dot:
                if abs(prev - i) > pi / 2:
                    return -1
                dot = angles[i][0]
                if self.are_close(prev_dot, dot):
                    ans2.append(dot)
                    prev = i
                    prev_dot = dot

        def check_circle(ans):
            first = False
            second = False
            third = False
            fourth = False
            for xx, yy in ans:
                if xx - x >= 0 and yy - y >= 0:
                    first = True
                if xx - x >= 0 and yy - y <= 0:
                    second = True
                if xx - x <= 0 and yy - y >= 0:
                    third = True
                if xx - x <= 0 and yy - y <= 0:
                    fourth = True
            return first and second and third and fourth

        if len(ans2) > 0:
            if len(ans1) + len(ans2) < 4:
                return -1
            while len(ans2) > 0 and not self.are_close(ans1[-1], ans2[-1]):
                ans2.pop()
            if len(ans2) != 0:
                if self.are_close(ans1[-1], ans2[-1]):
                    ans = ans1 + ans2
                    if check_circle(ans):
                        return ans
                return -1
        if len(ans1) < 4:
            return -1
        if self.are_close(ans1[0], ans1[-1]):
            if check_circle(ans1):
                return ans1
        return -1
            


    def put_dot(self, pos):
        if pos in self.used:
            return

        self.used.append(pos)
        self.dots[self.turn].append(pos)

        comp = self.get_next_component_value(self.turn)
        self.table[pos[0]][pos[1]] = comp
        self.components[comp] = pos

        to_refill = set()
        for ax, ay in moves8:
            nx, ny = pos[0] + ax, pos[1] + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if self.table[nx][ny] < 0:
                continue
            to_refill.add(self.table[nx][ny])
        to_refill.add(self.table[pos[0]][pos[1]])

        self.refill_components(to_refill)

        for comp in list(self.components):
            if comp in self.components:
                res = self.check_part_two(comp)
                if res != -1:
                    self.fill_component(self.components[comp], -2)
                    del self.components[comp]

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
    game = Game(20, 20)
    game.start()