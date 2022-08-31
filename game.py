from queue import Queue
import pygame
import sys
from copy import deepcopy
import properties
from game_drawer import draw_env


PVP = 0
PVC = 1
SANDBOX = 2

BLUE_PLAYER = 0
RED_PLAYER = 1


class Game:
    def __init__(
        self,
        linesX: int=39, linesY: int=32,
        game_mode: int=PVP,
        computer=None, is_computer_first: bool=False,
            names: tuple=("Синие", "Красные")):
        """Инициализирует игру."""

        #  Количество линий по ОХ.
        self.linesX = linesX
        #  Количество линий по ОY.
        self.linesY = linesY
        #  Режим игры.
        self.game_mode = game_mode
        #  Флаг, означающий, ходит ли компьютер первым.
        self.is_computer_first = is_computer_first

        #  Чей ход.
        self.turn = BLUE_PLAYER
        #  Список активных точек.
        self.dots = [[], []]
        #  Список захваченных точек.
        self.occupied_dots = [[], []]
        #  Ни кем не захваченные, но туда ходить нельзя.
        self.other_dots = []
        #  Список многоугольников
        self.polygons = []
        #  Счёт игроков.
        self.score = [0, 0]

        #  Массив для undo.
        self.history_undo = []
        #  Массив для redo.
        self.history_redo = []

        #  Инициализированный компьютер.
        self.computer = computer
        #  Имена игроков.
        self.names = names
        #  Размер окна по ОХ.
        x = (properties.BLOCK_SIZE * (self.linesX - 1) +
             properties.GAP * 2)
        #  Размер окна по ОУ.
        y = (properties.UP_LENGTH +
             properties.BLOCK_SIZE * (self.linesY - 1) +
             2 * properties.GAP)
        #  Размер окна.
        self.size = [x, y]
        self.screen = pygame.display.set_mode(self.size)
        self.timer = pygame.time.Clock()

    def get_neighbours(self, table: list, x: int, y: int):
        """Возвращает список достижимых соседей.

        Args:
            table (list): Игровое поле.
            -1 - точка пустая, 1 - стена, другое - заполненная.
            x (int): Координата по ОХ.
            y (int): Координата по ОY.

        Returns:
            list((int, int)): Массив точек.
        """
        #  Списки для генерации координат соседних клеток.
        #  Cлева, сверху, справа, снизу. (прямые)
        moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]
        #  Наискосок.
        moves4x = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        res = []
        #  Перебирает прямых соседей.
        #  Проверяет выход за таблицу и является ли клетка пустой.
        for ax, ay in moves4:
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if table[nx][ny] != -1:
                continue
            res.append((nx, ny))
        #  Перебирает соседей наискосок.
        #  Проверяет выход за таблицу, является ли клетка пустой.
        #  Проверяет не являются ли 2 соседние-наискосок клетки стенами
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

    def bfs(self, table: list, x: int, y: int, val: int=0):
        """Заполняет все пустые клетки значением val,
           начиная от точки (x, y).

        Args:
            table (list): Игровое поле.
            -1 - точка пустая, 1 - стена, другое - заполненная.
            x (int): Координата по ОХ.
            y (int): Координата по ОY.
            val (int, optional): Значение, которым заполняется. Defaults to 0.
        """
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

    def circle_sort(self, polygon: list):
        """Сортирует многоугольник по часовой стрелки,
           чтобы он нормально прорисовывался.

        Args:
            polygon (list): Массив точек.

        Returns:
            list((int, int)): Массив точек.
        """
        res = []
        current = polygon[0]
        #  Текущую точку удаляет из старого массива.
        #  К текущей точке находит самую ближнюю из оставшихся.
        #  Найденная точка становится текущей.
        #  Выполняется пока 2 и больше элемента в старом массиве.
        #  Оставшуюся точку просто добавляет в новый массив.
        #  Она замыкает окружность.
        while len(polygon) > 1:
            res.append(current)
            x, y = current
            polygon.remove(current)
            neigh = []
            for dot in polygon:
                dist = ((dot[0] - x) ** 2 + (dot[1] - y) ** 2) ** 0.5
                neigh.append((dist, dot))
            current = sorted(neigh)[0][1]
        res.append(current)
        return res

    def build_cover(self, table, current, component):
        def get_count(x, y):
            dot = None
            count = 0
            if x - 1 >= 0 and table[x - 1][y] == component:
                count += 1
            else:
                dot = (x - 1, y)
            if x + 1 < self.linesX and table[x + 1][y] == component:
                count += 1
            else:
                dot = (x + 1, y)
            if y - 1 >= 0 and table[x][y - 1] == component:
                count += 1
            else:
                dot = (x, y - 1)
            if y + 1 < self.linesY and table[x][y + 1] == component:
                count += 1
            else:
                dot = (x, y + 1)
            return count, dot

        polygon = []
        for x in range(self.linesX):
            for y in range(self.linesY):
                if table[x][y] == 1:
                    count, dot = get_count(x, y)
                    if count == 3:
                        if get_count(dot[0], dot[1])[0] == 0:
                            polygon.append((x, y))
                    elif count > 0 and count != 4:
                        polygon.append((x, y))
                if table[x][y] == component:
                    self.other_dots.append((x, y))

        if polygon:
            sorted_polygon = self.circle_sort(polygon)
            self.polygons.append((sorted_polygon, current))

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
                    if (x, y) in self.occupied_dots[current]:
                        self.occupied_dots[current].remove((x, y))
                        self.dots[current].append((x, y))
                        self.score[enemy] -= 1
                    if (x, y) in self.dots[enemy]:
                        to_fill.append((x, y))
                        self.dots[enemy].remove((x, y))
                        self.occupied_dots[enemy].append((x, y))
                        self.score[current] += 1

        count = 2
        for x, y in to_fill:
            if table[x][y] == -1:
                self.bfs(table, x, y, count)
                count += 1

        for component in range(2, count + 1):
            self.build_cover(table, current, component)

    def is_avilable(self, pos):
        return (
            pos not in self.dots[0] and
            pos not in self.dots[1] and
            pos not in self.occupied_dots[0] and
            pos not in self.occupied_dots[1] and
            pos not in self.other_dots)

    def save_current(self):
        self.history_redo = []
        note = []
        note.append(self.turn)
        note.append(deepcopy(self.dots))
        note.append(deepcopy(self.occupied_dots))
        note.append(deepcopy(self.other_dots))
        note.append(self.polygons.copy())
        note.append(self.score.copy())
        self.history_undo.append(note)

    def undo(self):
        if len(self.history_undo) >= 2:
            self.history_redo.append(deepcopy(self.history_undo[-1]))
            self.history_undo = self.history_undo[:-1]
            note = deepcopy(self.history_undo[-1])
            self.turn = note[0]
            self.dots = note[1]
            self.occupied_dots = note[2]
            self.other_dots = note[3]
            self.polygons = note[4]
            self.score = note[5]

    def redo(self):
        if self.history_redo:
            note = deepcopy(self.history_redo[-1])
            self.history_redo = self.history_redo[:-1]
            self.history_undo.append(deepcopy(note))
            self.turn = note[0]
            self.dots = note[1]
            self.occupied_dots = note[2]
            self.other_dots = note[3]
            self.polygons = note[4]
            self.score = note[5]

    def put_dot(self, pos, history_lock=False):
        self.dots[self.turn].append(pos)

        self.check(self.turn)
        self.check((self.turn + 1) % 2)

        if self.game_mode != SANDBOX:
            self.turn += 1
            self.turn %= 2

        if not history_lock:
            self.save_current()

    def get_mouse_pos(self, pos):
        x = ((pos[0] - properties.GAP) /
             properties.BLOCK_SIZE)
        y = ((pos[1] - properties.GAP - properties.UP_LENGTH) /
             properties.BLOCK_SIZE)
        delta = 0.3
        a = x % 1 <= delta or x % 1 >= (1 - delta)
        b = y % 1 <= delta or y % 1 >= (1 - delta)
        if not (a and b):
            return None
        x = round(x)
        y = round(y)
        if x < 0 or x >= self.linesX or y < 0 or y >= self.linesY:
            return None
        return x, y

    def start(self):
        pygame.init()
        pos = None
        amount = self.linesX * self.linesY
        if self.game_mode == PVC and self.is_computer_first:
            self.put_dot(
                (self.linesX // 2, self.linesY // 2),
                history_lock=True)
        self.save_current()
        while True:
            count = (len(self.dots[0]) +
                     len(self.dots[1]) +
                     len(self.other_dots))
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
                    if event.key == pygame.K_u:
                        self.undo()
                    if event.key == pygame.K_r:
                        self.redo()
                pos = self.get_mouse_pos(pygame.mouse.get_pos())
                if not self.is_avilable(pos):
                    pos = None
                if event.type == pygame.MOUSEBUTTONUP:
                    if pos is None:
                        continue
                    if self.game_mode == PVP:
                        if event.button == 1:
                            self.put_dot(pos)
                    if self.game_mode == PVC:
                        if event.button == 1:
                            self.put_dot(pos)
                            computer_pos = self.computer.move(pos)
                            if computer_pos is not None:
                                self.put_dot(
                                    computer_pos,
                                    history_lock=True)
                    if self.game_mode == SANDBOX:
                        if event.button == 1:
                            self.turn = BLUE_PLAYER
                            self.put_dot(pos)
                        if event.button == 3:
                            self.turn = RED_PLAYER
                            self.put_dot(pos)

            self.timer.tick(60)
            draw_env(
                self.screen, self.size, pos,
                self.linesX, self.linesY, self.game_mode,
                self.turn,
                self.dots, self.occupied_dots,
                self.polygons,
                self.score,
                self.names)
            pygame.display.flip()
