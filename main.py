import pygame

from colors import *

moves8 = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, 1], [1, -1]]

class Game:
    def __init__(self):
        self.up_length = 100
        self.blocksX = 30
        self.blocksY = 10
        self.block_size = 25
        self.up_length = 100
        self.gap = 50
        self.dots = [[], []]
        self.turn = 0
        self.last = -1
        self.size = [self.block_size * self.blocksX + self.gap * 2,
                     self.up_length + self.block_size * self.blocksY + 2 * self.gap]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()

    def draw_window(self):
        self.screen.fill(Color.white)
        pygame.draw.rect(self.screen, Color.up_menu,
                            [0, 0, self.size[0], self.up_length])

    def draw_env(self):
        for column in range(self.blocksX + 1):
            self.draw_vertical_line(Color.black, column)
        for row in range(self.blocksY + 1):
            self.draw_horizontal_line(Color.black, row)

        for dot in self.dots[0]:
            self.draw_dot(Color.red, dot[0], dot[1])
        for dot in self.dots[1]:
            self.draw_dot(Color.blue, dot[0], dot[1])

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
        score = 555
        text_score = courier.render(f"Score: {score}", 0, Color.white)
        self.screen.blit(text_score, (20, 20))

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

    def dfs(self, pos):
        x = pos[0]
        y = pos[1]
        for dx, dy in moves8:
            npos = x + dx, y + dy
            if npos in self.dots[self.turn]:
                pass

    def handle_put(self, pos):
        self.dfs(pos)

    def put_dot(self, pos):
        if pos in self.dots[0] or pos in self.dots[1]:
            return

        if self.turn == 0:
            self.dots[0].append(pos)
            self.last = pos

            self.handle_put(pos)

            self.turn = 1
        else:
            self.dots[1].append(pos)
            self.last = pos

            self.handle_put(pos)

            self.turn = 0

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
            ev = pygame.event.get()

            for event in ev:
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