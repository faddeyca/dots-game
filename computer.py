import random
from copy import deepcopy
from properties import Properties as p


class Robot:
    def __init__(self, robot_mode):
        self.robot_mode = robot_mode
        self.game = None

    def load_game(self, game):
        self.game = game

    def move(self, pos=None):
        if self.robot_mode == 0:
            return self.random_move()
        else:
            return self.smart_move(pos)

    def get_neighbours(self, x, y):
        moves8 = [[-1, -1], [-1, 1], [1, -1], [1, 1],
                  [-1, 0], [0, -1], [0, 1], [1, 0]]
        res = [[], [], []]
        enemy = (self.game.turn + 1) % 2
        for ax, ay in moves8:
            nx, ny = x + ax, y + ay
            if (nx < 0 or nx >= self.game.linesX or
               ny < 0 or ny >= self.game.linesY):
                continue
            dot = (nx, ny)
            if dot in self.game.dots[self.game.turn]:
                res[0].append(dot)
            elif dot in self.game.dots[enemy]:
                res[1].append(dot)
            elif (dot not in self.game.dots[self.game.turn] and
                  dot not in self.game.dots[enemy + 2] and
                  dot not in self.game.dots[4]):
                res[2].append(dot)
        return res

    def random_move(self):
        possible_pos = set()
        enemy = (self.game.turn + 1) % 2
        for x, y in self.game.dots[enemy]:
            neigh = self.get_neighbours(x, y)[2]
            for dot in neigh:
                possible_pos.add(dot)
        if len(possible_pos) == 0:
            return -1

        possible_pos = list(possible_pos)

        i = random.randint(0, len(possible_pos) - 1)
        return possible_pos[i]

    def smart_move(self, pos):
        possible_pos = set()
        current = self.game.turn
        enemy = (self.game.turn + 1) % 2
        for x, y in self.game.dots[enemy]:
            neigh = self.get_neighbours(x, y)[2]
            for dot in neigh:
                possible_pos.add(dot)
        if len(possible_pos) == 0:
            return -1
        pre_possible_pos = list(possible_pos)

        possible_pos = []
        count = 3
        while len(possible_pos) == 0:
            for x, y in pre_possible_pos:
                if abs(x - pos[0]) <= count and abs(y - pos[1]) <= count:
                    possible_pos.append((x, y))
            count += 1

        currscore = self.game.score[enemy]

        def save_prev():
            self.prev_turn = self.game.turn
            self.prev_dots = deepcopy(self.game.dots)
            self.prev_polygons = self.game.polygons.copy()
            self.prev_score = self.game.score.copy()

        def load_prev():
            self.game.turn = self.prev_turn
            self.game.dots = self.prev_dots
            self.game.polygons = self.prev_polygons
            self.game.score = self.prev_score

        actions = []
        for dot in possible_pos:
            save_prev()
            self.game.turn += 1
            self.game.turn %= 2
            self.game.put_dot(dot, lock=True)
            res = self.game.score[enemy] - currscore
            if res > 0:
                load_prev()
                actions.append((res * p.defence_priority, dot))
            load_prev()

        currscore = self.game.score[self.game.turn]
        for dot in possible_pos:
            save_prev()
            self.game.put_dot(dot, lock=True)
            res = self.game.score[current] - currscore
            if res > 0:
                load_prev()
                actions.append((res * p.attack_priority, dot))
            load_prev()

        if len(actions) == 0:
            i = random.randint(0, len(possible_pos) - 1)
            return possible_pos[i]
        else:
            return sorted(actions)[-1][1]
