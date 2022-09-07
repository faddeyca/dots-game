from queue import Queue
import pygame
import sys
from copy import deepcopy
import properties
from game_drawer import draw_env


BLUE_PLAYER = 0
RED_PLAYER = 1


class Game:
    def __init__(
        self,
        linesX: int = 39, linesY: int = 32,
        game_mode: str = "PVP",
        computer=None, is_computer_first: bool = False,
            names: tuple = ("Синие", "Красные")):
        """
        Инициализирует игру.
        """

        #  Количество точек по ОХ.
        self.linesX = linesX
        #  Количество точек по ОY.
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
        """
        Возвращает список соседей.

        Args:
            table (list): Игровое поле.
            -1 - точка пустая, 1 - стена, другое - заполненная.
            x (int): Координата точки по ОХ.
            y (int): Координата точки по ОY.

        Returns:
            list((int, int)): Массив точек.
        """
        #  Cлева, сверху, справа, снизу.
        moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]
        res = []
        for ax, ay in moves4:
            """
            Перебирает соседей.
            Проверяет выход за таблицу и является ли точка пустой.
            """
            nx, ny = x + ax, y + ay
            if nx < 0 or nx >= self.linesX or ny < 0 or ny >= self.linesY:
                continue
            if table[nx][ny] != -1:
                continue
            res.append((nx, ny))
        return res

    def bfs(self, table: list, x: int, y: int, val: int = 0):
        """
        Заполняет все пустые клетки значением val,
        начиная от точки (x, y).

        Args:
            table (list): Игровое поле.
            -1 - точка пустая, 1 - стена, другое - заполненная.
            x (int): Координата точки по ОХ.
            y (int): Координата точки по ОY.
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
        """
        Сортирует многоугольник по часовой стрелки,
        чтобы он нормально прорисовывался.

        Args:
            polygon (list): Массив точек.

        Returns:
            list((int, int)): Массив точек.
        """
        res = []
        current = polygon[0]
        while len(polygon) > 1:
            """
            Текущую точку удаляет из старого массива.
            К текущей точке находит самую ближнюю из оставшихся.
            Найденная точка становится текущей.
            Выполняется пока 2 и больше элемента в старом массиве.
            Оставшуюся точку просто добавляет в новый массив.
            Она замыкает окружность.
            """
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

    def build_cover(self, table: list, current: int, component: int):
        """
        Строит оболочку вокруг захваченных зон.

        Args:
            table (list): Игровое поле.
            current (int): Текущий игрок.
            component (int): Номер окружённой зоны.
        """
        def get_count(x: int, y: int):
            """Возвращает число соседних клеток,
               которые находятся в окружённой зоне.

            Args:
                x (int): Координата по ОХ.
                y (int): Координата по ОН.

            Returns:
                int: Число соседей.
            """
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
                """
                Перебирает поле.
                Добавляет стену в многоугольник, если
                она граничит с окружённой зоной, но
                не окружена ею, а в случае если окружена
                окружённой зоной с 3 сторон, то 4
                сосед это не стена.
                """
                if table[x][y] == 1:
                    count, dot = get_count(x, y)
                    if count == 3:
                        if get_count(dot[0], dot[1])[0] == 0:
                            polygon.append((x, y))
                    elif count > 0 and count != 4:
                        polygon.append((x, y))
                #  Также блокирует пустые клетки,
                #  которые попали в оккупированную зону.
                if table[x][y] == component:
                    self.other_dots.append((x, y))

        if polygon:
            sorted_polygon = self.circle_sort(polygon)
            self.polygons.append((sorted_polygon, current))

    def check(self, current: int):
        """
        Проверяет не окружил ли текущий игрок соперника.
        От всех краёв запсукается обход в ширину.
        В итоге, если нашлась незаполненная точка, то
        это значит, что эта точка попадает под окружение
        текущего игрока, и если там стоит точка противника, то
        она объявляется захваченной.

        Args:
            current (int): Текущий игрок.
        """
        #  Игровое поле
        table = []
        for x in range(self.linesX):
            """
            Строит игровое поле по текущему игроку.
            То есть на поле есть только точки текущего игрока(1).
            Остальные - пустое пространство(-1).
            """
            line = []
            for y in range(self.linesY):
                if (x, y) in self.dots[current]:
                    line.append(1)
                else:
                    line.append(-1)
            table.append(line)

        """
        Перебираются точки по рамке поля.
        Если попадается пустая точка, то от нее запускается
        обход в ширину, и все доступные точки заполняются 0.
        """
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

        """
        Перебирается всё поле. В массив добавляются
        незаполненные точки, в которых есть точка противника.
        Также из под захвата освобождаются собственные точки.
        """
        to_fill = []
        enemy = (current + 1) % 2
        for x in range(self.linesX):
            for y in range(self.linesY):
                if table[x][y] == -1:
                    if (x, y) in self.dots[enemy]:
                        to_fill.append((x, y))
                        self.dots[enemy].remove((x, y))
                        self.occupied_dots[enemy].append((x, y))
                        self.score[current] += 1
                    if (x, y) in self.occupied_dots[current]:
                        self.occupied_dots[current].remove((x, y))
                        self.dots[current].append((x, y))
                        self.score[enemy] -= 1

        """
        Заполняет все захваченные зоны, в которых
        оказалась точка противника уникальным числом.
        То есть каждая такая зона - отдельная компонента связности.
        """
        count = 2
        for x, y in to_fill:
            if table[x][y] == -1:
                self.bfs(table, x, y, count)
                count += 1

        """
        Вокруг каждой компоненты независимо строится
        многоугольник.
        """
        for component in range(2, count + 1):
            self.build_cover(table, current, component)

    def is_free(self, pos: tuple):
        """
        Проверяет не находится ли точка
        хотя бы в одном из массивов точек.

        Args:
            pos ((int, int)): Координаты точки.

        Returns:
            bool: Результат проверки.
        """
        return (
            pos not in self.dots[0] and
            pos not in self.dots[1] and
            pos not in self.occupied_dots[0] and
            pos not in self.occupied_dots[1] and
            pos not in self.other_dots)

    def save_current(self):
        """
        Сохраняет текущее состояние игры.
        """
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
        """
        Возвращает состояние игры к предыдущему.
        """
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
        """
        Возвращает состояние игры к новому, после undo.
        """
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

    def put_dot(self, pos: tuple, history_lock: bool = False):
        """
        Совершает ход.
        То есть тсавит точку и выполняет действия.

        Args:
            pos ((int, int)): Координаты точки.
            history_lock (bool, optional):
            Блокировка записи в историю. Defaults to False.
        """
        #  Добвляется к активным точкам текущего игрока.
        self.dots[self.turn].append(pos)

        #  Проверяет окружил ли текущий игрок противника.
        self.check(self.turn)
        #  Проверяет не попала ли точка в окружение противника.
        self.check((self.turn + 1) % 2)

        #  Если режим игры не песочница, то переключает ход.
        if self.game_mode != "SB":
            self.turn += 1
            self.turn %= 2

        #  Сохраняет текущее состояние игры,
        #  если нет флага, запрещающего это.
        if not history_lock:
            self.save_current()

    def get_mouse_pos(self, pos: tuple):
        """
        Возвращает позицию курсора в треминах
        координат игрового поля.

        Args:
            pos ((int, int)): Координаты мышки.
            Относительно игрового окна.

        Returns:
            (int, int): Координаты точки.
        """
        #  Координаты в клетках.
        #  Могут быть дробными.
        x = ((pos[0] - properties.GAP) /
             properties.BLOCK_SIZE)
        y = ((pos[1] - properties.GAP - properties.UP_LENGTH) /
             properties.BLOCK_SIZE)
        #  Окрестность нажатия.
        delta = 0.3
        #  Если координаты мышки не больше чем delta
        #  по каждой оси от какой-то точки, то
        #  выбирается эта точка.
        a = x % 1 <= delta or x % 1 >= (1 - delta)
        b = y % 1 <= delta or y % 1 >= (1 - delta)
        if not (a and b):
            return None
        x = round(x)
        y = round(y)
        if x < 0 or x >= self.linesX or y < 0 or y >= self.linesY:
            return None
        #  Также выбранная точка должна быть свободной.
        if not self.is_free((x, y)):
            return None
        return x, y

    def start(self):
        pygame.init()
        #  Текущая позиция курсора.
        pos = None
        #  Количество точек всего.
        amount = self.linesX * self.linesY
        #  Первый ход компьютера.
        if self.game_mode == "PVC" and self.is_computer_first:
            self.put_dot(
                (self.linesX // 2, self.linesY // 2),
                history_lock=True)
        #  Сохраняется начальное состояние игры.
        self.save_current()
        while True:
            count = (len(self.dots[0]) +
                     len(self.dots[1]) +
                     len(self.other_dots))
            #  Если не осталось свободных точек, то игра заканчивается.
            if count == amount:
                return self.score
            events = pygame.event.get()
            pos = self.get_mouse_pos(pygame.mouse.get_pos())
            for event in events:
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return self.score
                        if event.key == pygame.K_u:
                            self.undo()
                        if event.key == pygame.K_r:
                            self.redo()
                    case pygame.MOUSEBUTTONUP:
                        if pos is None:
                            continue
                        match self.game_mode:
                            case "PVP":
                                if event.button == 1:
                                    self.put_dot(pos)
                            case "PVC":
                                if event.button == 1:
                                    self.put_dot(
                                        pos,
                                        history_lock=True)
                                    computer_pos = self.computer.move(pos)
                                    if computer_pos is not None:
                                        self.put_dot(computer_pos)
                            case "SB":
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
