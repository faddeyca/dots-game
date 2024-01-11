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
            names: tuple = ("Blue", "Red")):
        """
        Initializes the game.
        """

        #  Amount of dots by Х-axis.
        self.linesX = linesX
        #  Amount of dots by Y-axis.
        self.linesY = linesY
        #  Game mode
        self.game_mode = game_mode
        #  Flag indicating whether the computer moves first.
        self.is_computer_first = is_computer_first

        #  Whose turn it is.
        self.turn = BLUE_PLAYER
        #  List of active points.
        self.dots = [[], []]
        #  List of captured points.
        self.occupied_dots = [[], []]
        #  Points that are not captured by anyone but cannot be moved to.
        self.other_dots = []
        #  List of polygons.
        self.polygons = []
        #  Players' scores.
        self.score = [0, 0]

        #  List for undo.
        self.history_undo = []
        #  List for redo.
        self.history_redo = []

        #  Initialized computer.
        self.computer = computer
        #  Players' names.
        self.names = names
        #  Windows size by Х-axis.
        x = (properties.BLOCK_SIZE * (self.linesX - 1) +
             properties.GAP * 2)
        #  Windows size by Y-axis.
        y = (properties.UP_LENGTH +
             properties.BLOCK_SIZE * (self.linesY - 1) +
             2 * properties.GAP)
        #  Windows size.
        self.size = [x, y]
        self.screen = pygame.display.set_mode(self.size, depth=12, vsync=1)
        self.timer = pygame.time.Clock()

    def get_neighbours(self, table: list, x: int, y: int):
        """
       Returns a list of neighbors.

        Args:
            table (list): Game field.
            -1 - empty point, 1 - wall, other values - filled.
            x (int): Point's coordinate along the X-axis.
            y (int): Point's coordinate along the Y-axis.

        Returns:
            list((int, int)): Dots' array.
        """
        #  Cлева, сверху, справа, снизу.
        moves4 = [[-1, 0], [0, -1], [0, 1], [1, 0]]
        res = []
        for ax, ay in moves4:
            """
            Iterates over neighbors.
            Checks for out-of-bounds and whether the point is empty.
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
        Fills all empty cells with the value val,
        starting from the point (x, y).

        Args:
            table (list): Game field.
            -1 - empty point, 1 - wall, other values - filled.
            x (int): Point's coordinate along the X-axis.
            y (int): Point's coordinate along the Y-axis.
            val (int, optional): Value to fill with. Defaults to 0.
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
        Sorts the polygon clockwise to ensure it is drawn correctly.

        Args:
            polygon (list): Dots' array.

        Returns:
            list((int, int)): Dots' array.
        """
        res = []
        current = polygon[0]
        while len(polygon) > 1:
            """
            The current point is removed from the old array.
            The closest point to the current one is found among the remaining points.
            The found point becomes the current one.
            This is done as long as there are 2 or more elements in the old array.
            The remaining point is simply added to the new array.
            It closes the loop.
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
        Builds a hull around captured areas.

        Args:
            table (list): Game field.
            current (int): Current player.
            component (int): Number of the surrounded area.
        """
        def get_count(x: int, y: int):
            """
            Returns the number of neighboring cells
            that are in the surrounded area.

            Args:
                x (int): Coordinate along the X-axis.
                y (int): Coordinate along the Y-axis.

            Returns:
                int: Number of neighbors.
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
                Iterates over the field.
                Adds a wall to the polygon if
                it borders a surrounded area but
                is not surrounded by it, and in the case
                where it is surrounded by the surrounded area
                on 3 sides, the 4th neighbor is not a wall.
                """
                if table[x][y] == 1:
                    count, dot = get_count(x, y)
                    if count == 3:
                        if get_count(dot[0], dot[1])[0] == 0:
                            polygon.append((x, y))
                    elif count > 0 and count != 4:
                        polygon.append((x, y))
                #  Also blocks empty cells
                #  that have entered the occupied area.
                if table[x][y] == component:
                    self.other_dots.append((x, y))

        if polygon:
            sorted_polygon = self.circle_sort(polygon)
            self.polygons.append((sorted_polygon, current))

    def check(self, current: int):
        """
        Checks whether the current player has surrounded the opponent.
        A breadth-first search is launched from all edges.
        In the end, if an unoccupied point is found, it means that
        this point falls under the surround of the current player,
        and if there is an opponent's point there, it is declared captured

        Args:
            current (int): Current player.
        """
        #  Игровое поле
        table = []
        for x in range(self.linesX):
            """
            Builds the game field for the current player.
            That is, the field only contains points of the current player (1).
            Others are empty spaces (-1).
            """
            line = []
            for y in range(self.linesY):
                if (x, y) in self.dots[current]:
                    line.append(1)
                else:
                    line.append(-1)
            table.append(line)

        """
        Iterates over the points along the border of the field.
        If an empty point is encountered, a breadth-first search is launched from it,
        and all accessible points are filled with 0.
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
        Iterates over the entire field. Unfilled points that contain an opponent's point are added to the array.
        Also, own points are freed from capture.
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
        Fills all captured areas in which
        an opponent's point has ended up with a unique number.
        Each such area is a separate connected component.
        """
        count = 2
        for x, y in to_fill:
            if table[x][y] == -1:
                self.bfs(table, x, y, count)
                count += 1

        """
        A polygon is independently constructed around each component.
        """
        for component in range(2, count + 1):
            self.build_cover(table, current, component)

    def is_free(self, pos: tuple):
        """
        Checks if the point is in at least one of the arrays of points.

        Args:
            pos ((int, int)): Point coordinates.

        Returns:
            bool: Result of the check.
        """
        return (
            pos not in self.dots[0] and
            pos not in self.dots[1] and
            pos not in self.occupied_dots[0] and
            pos not in self.occupied_dots[1] and
            pos not in self.other_dots)

    def save_current(self):
        """
        Saves the current state of the game.
        """
        if self.game_mode == "ONLINE":
            return
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
        Returns the game state to the previous one.
        """
        if self.game_mode == "ONLINE":
            return
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
        Returns the game state to a new one after undo.
        """
        if self.game_mode == "ONLINE":
            return
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
        Makes a move.
        That is, places a point and performs actions.

        Args:
            pos ((int, int)): Point coordinates.
            history_lock (bool, optional):
            Lock for recording in history. Defaults to False.
        """
        #  Added to the active points of the current player.
        self.dots[self.turn].append(pos)

        #  Checks whether the current player has surrounded the opponent.
        self.check(self.turn)
        #  Checks whether the point has fallen into the opponent's surround.
        self.check((self.turn + 1) % 2)

        #  If the game mode is not sandbox, then switch turns.
        if self.game_mode != "SB":
            self.turn += 1
            self.turn %= 2

        #  Saves the current state of the game,
        #  if there is no flag preventing it.
        if not history_lock:
            self.save_current()

    def get_mouse_pos(self, pos: tuple):
        """
        Returns the cursor position in terms of
        game field coordinates.

        Args:
            pos ((int, int)): Mouse coordinates.
            Relative to the game window.

        Returns:
            (int, int): Point coordinates.
        """
        #  Coordinates in cells.
        #  Can be fractional.
        x = ((pos[0] - properties.GAP) /
             properties.BLOCK_SIZE)
        y = ((pos[1] - properties.GAP - properties.UP_LENGTH) /
             properties.BLOCK_SIZE)
        #  Neighborhood of the click.
        delta = 0.3
        #  If the mouse coordinates are not greater than delta
        #  in each axis from some point, then
        #  that point is selected.
        a = x % 1 <= delta or x % 1 >= (1 - delta)
        b = y % 1 <= delta or y % 1 >= (1 - delta)
        if not (a and b):
            return None
        x = round(x)
        y = round(y)
        if x < 0 or x >= self.linesX or y < 0 or y >= self.linesY:
            return None
        #  The selected point should also be free.
        if not self.is_free((x, y)):
            return None
        return x, y

    def start(self, sc=None, turn=None):
        pygame.init()
        #  Current cursor position.
        pos = None
        #  Total number of points.
        amount = self.linesX * self.linesY
        #  The computer's first move.
        if self.game_mode == "PVC" and self.is_computer_first:
            self.put_dot(
                (self.linesX // 2, self.linesY // 2),
                history_lock=True)
        #  The initial state of the game is saved.
        self.save_current()
        while True:
            if self.game_mode == "ONLINE" and turn == 1:
                x = int(str(sc.recv(1024).decode()))
                if x == -1:
                    return self.score
                y = int(str(sc.recv(1024).decode()))
                pos = (x, y)
                self.put_dot(pos)
                turn = 0
            count = (len(self.dots[0]) +
                     len(self.dots[1]) +
                     len(self.other_dots))
            #  If there are no more free points, the game ends.
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
                            if self.game_mode == "ONLINE":
                                sc.send(bytes(str(-1).encode()))
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
                            case "ONLINE":
                                if event.button == 1:
                                    self.put_dot(pos)
                                    sc.send(bytes(str(pos[0]).encode()))
                                    sc.send(bytes(str(pos[1]).encode()))
                                    turn = 1

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
