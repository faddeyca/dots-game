import random
from copy import deepcopy
import properties


class Computer:
    def __init__(self, robot_mode: int):
        self.robot_mode = robot_mode
        self.game = None

    def load_game(self, game):
        self.game = game

    def move(self, player_pos: int=None):
        if self.robot_mode == 0:
            return self.random_move()
        else:
            return self.smart_move(player_pos)

    def get_neighbours(self, x: int, y: int):
        """Возвращает список незанятых точек по соседству с точкой.
        Args:
            x (int): Х координата.
            y (int): У координата.

        Returns:
            list((int, int)): Список пар (X, Y).
        """
        #  Список для генерации координат соседних клеток.
        moves8 = [[-1, -1], [-1, 1], [1, -1], [1, 1],
                  [-1, 0], [0, -1], [0, 1], [1, 0]]
        result = []
        computer = self.game.turn
        player = (self.game.turn + 1) % 2

        #  Перебор соседних клеток и их проверка.
        for ax, ay in moves8:
            nx, ny = x + ax, y + ay
            if (nx < 0 or nx >= self.game.linesX or
                    ny < 0 or ny >= self.game.linesY):
                continue
            dot = (nx, ny)
            if (dot not in self.game.dots[computer] and
                    dot not in self.game.dots[player] and
                    dot not in self.game.occupied_dots[computer] and
                    dot not in self.game.occupied_dots[player] and
                    dot not in self.game.other_dots):
                result.append(dot)
        return result

    def get_possible_pos(self):
        """Возвращает список всех незанятых точек по соседству со всеми точками игрока.

        Returns:
            list((int, int)): Список пар (X, Y).
        """
        #  Множество незанятых точек.
        #  Используется Set так как могут быть повторения.
        possible_pos = set()
        player = (self.game.turn + 1) % 2
        #  Перебор точек игрока.
        #  Добавление подходящих соседних точек в множество.
        for x, y in self.game.dots[player]:
            neigh = self.get_neighbours(x, y)
            for dot in neigh:
                possible_pos.add(dot)
        return list(possible_pos)

    def random_move(self):
        """Выбирает случайную точку из списка незанятых точек.

        Returns:
            (int, int): Пара (X, Y).
        """
        possible_pos = self.get_possible_pos()
        if not possible_pos:
            return None

        return random.choice(possible_pos)

    def smart_move(self, player_pos: tuple):
        """Выбирает самый оптимальный ход для компьютера.
           Перебирает и сравнивает по эффективности возможные ходы.

        Args:
            player_pos (int, int): Последний ход игрока.

        Returns:
            (int, int): Пара (X, Y).
        """
        computer = self.game.turn
        player = (self.game.turn + 1) % 2

        #  Список всех незанятых точек по соседству со всеми точками игрока.
        pre_possible_pos = self.get_possible_pos()
        if not pre_possible_pos:
            return None

        #  Выбирает точки, расстояние до которых не более
        #  CHECK_AREA от последнего хода игрока.
        #  Если не находит подходящих точек, то зона поиска расширяется.
        max_value = max(self.game.linesX, self.game.linesY) * 2
        possible_pos = []
        searching_zone = properties.CHECK_AREA
        while not possible_pos:
            for x, y in pre_possible_pos:
                if (abs(x - player_pos[0]) <= searching_zone and
                        abs(y - player_pos[1]) <= searching_zone):
                    possible_pos.append((x, y))
            searching_zone += 1
            if searching_zone > max_value:
                #  В теории случиться не должно.
                #  Можно добиться этой ошибки, подключив компьютер к песочнице.
                raise ValueError("Зона поиска слишком большая")

        #  Функция, сохраняющая текущее состояние игры в единичном экземпляре.
        def save_prev():
            self.prev_turn = self.game.turn
            self.prev_dots = deepcopy(self.game.dots)
            self.prev_occupied_dots = deepcopy(self.game.occupied_dots)
            self.prev_other_dots = deepcopy(self.game.other_dots)
            self.prev_polygons = self.game.polygons.copy()
            self.prev_score = self.game.score.copy()

        #  Функция загрузки сохранённого состояния игры.
        def load_prev():
            self.game.turn = self.prev_turn
            self.game.dots = self.prev_dots
            self.game.occupied_dots = self.prev_occupied_dots
            self.game.other_dots = self.prev_other_dots
            self.game.polygons = self.prev_polygons
            self.game.score = self.prev_score

        #  Текущий счёт игрока.
        currscore = self.game.score[player]

        #  Массив возможных ходов с коэфицентами эффективности. (int, dot)
        actions = []

        #  Рассматривает, повысится ли счёт игрока,
        #  если он поставит точку в dot.
        #  Если счёт игрока повышается,
        #  то компьютер может поставить туда точку, чтобы помешать.
        for dot in possible_pos:
            #  Сохранение текущего состояния.
            save_prev()
            #  Иммитация хода игрока.
            self.game.turn += 1
            self.game.turn %= 2
            self.game.put_dot(dot, history_lock=True)
            #  Разница между счётом игрока до и после иммитации его хода.
            res = self.game.score[player] - currscore
            #  Загрузка текущего состяния.
            load_prev()
            #  Если счёт игрока повысился,
            #  то ход записывается в возможные действия.
            #  Коэфицент эффективности = res * DEFENCE_PRIORITY
            if res > 0:
                actions.append((res * properties.DEFENCE_PRIORITY, dot))

        #  Текущий счёт компьютера.
        currscore = self.game.score[computer]

        #  Рассматривает, повысится ли счёт компьютера,
        #  если он поставит точку в dot.
        #  Если счёт компьютера повышается,
        #  то компьютер может поставить туда точку.
        for dot in possible_pos:
            #  Сохранение текущего состояния.
            save_prev()
            #  Иммитация хода игрока.
            self.game.put_dot(dot, history_lock=True)
            #  Разница между счётом компьютера до и после иммитации его хода.
            res = self.game.score[computer] - currscore
            #  Загрузка текущего состяния.
            load_prev()
            #  Если счёт компьютера повысился,
            #  то ход записывается в возможные действия.
            #  Коэфицент эффективности = res * DEFENCE_PRIORITY
            if res > 0:
                actions.append((res * properties.ATTACK_PRIORITY, dot))

        if not actions:
            #  Если никаких умных действий не нашлось,
            #  то компьютер ходит случайно.
            return random.choice(possible_pos)
        else:
            #  Компьютер выбирает самый эффективный ход.
            return sorted(actions)[-1][1]
