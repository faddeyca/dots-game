import random
from copy import deepcopy
import properties


class Computer:
    def __init__(self, robot_mode: int):
        self.robot_mode = robot_mode
        self.game = None

    def load_game(self, game):
        self.game = game

    def move(self, player_pos: int = None):
        if self.robot_mode == 0:
            return self.random_move()
        else:
            return self.smart_move(player_pos)

    def get_neighbours(self, x: int, y: int):
        """
        Returns a list of unoccupied points adjacent to the point.
        Args:
            x (int): Х-axis coordinate.
            y (int): У-axis coordinate.

        Returns:
            list((int, int)): List of tuples (X, Y).
        """
        #  List for generating coordinates of neighboring cells.
        moves8 = [[-1, -1], [-1, 1], [1, -1], [1, 1],
                  [-1, 0], [0, -1], [0, 1], [1, 0]]
        result = []
        computer = self.game.turn
        player = (self.game.turn + 1) % 2

        #  Iterating over neighboring cells and checking them.
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
        """
        Returns a list of all unoccupied points
        adjacent to all of the player's points.

        Returns:
            list((int, int)): List of tuples (X, Y).
        """
        #  Set of unoccupied points.
        #  A Set is used because there can be duplicates.
        possible_pos = set()
        player = (self.game.turn + 1) % 2
        #  Iterating over the player's points.
        #  Adding suitable neighboring points to the set.
        for x, y in self.game.dots[player]:
            neigh = self.get_neighbours(x, y)
            for dot in neigh:
                possible_pos.add(dot)
        return list(possible_pos)

    def random_move(self):
        """
        Selects a random point from the list of unoccupied points.

        Returns:
            (int, int): Tuple (X, Y).
        """
        possible_pos = self.get_possible_pos()
        if not possible_pos:
            return None

        return random.choice(possible_pos)

    def smart_move(self, player_pos: tuple):
        """
        Chooses the most optimal move for the computer.
        Iterates and compares the efficiency of possible moves.

        Args:
            player_pos (int, int): Last player's turn.

        Returns:
            (int, int): Tuple (X, Y).
        """
        computer = self.game.turn
        player = (self.game.turn + 1) % 2

        #  List of all unoccupied points adjacent to all of the player's points.
        pre_possible_pos = self.get_possible_pos()
        if not pre_possible_pos:
            return None

        #  Selects points that are no more than
        #  CHECK_AREA distance from the player's last move.
        #  If no suitable points are found, the search area is expanded.
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
                #  This should not happen in theory.
                #  This error can be achieved by connecting the computer to the sandbox.
                raise ValueError("The search area is too large.")

        #  Function that saves the current state of the game in a single instance.
        def save_prev():
            self.prev_turn = self.game.turn
            self.prev_dots = deepcopy(self.game.dots)
            self.prev_occupied_dots = deepcopy(self.game.occupied_dots)
            self.prev_other_dots = deepcopy(self.game.other_dots)
            self.prev_polygons = self.game.polygons.copy()
            self.prev_score = self.game.score.copy()

        #  Function for loading the saved state of the game.
        def load_prev():
            self.game.turn = self.prev_turn
            self.game.dots = self.prev_dots
            self.game.occupied_dots = self.prev_occupied_dots
            self.game.other_dots = self.prev_other_dots
            self.game.polygons = self.prev_polygons
            self.game.score = self.prev_score

        #  Current player's score.
        currscore = self.game.score[player]

        #  Array of possible moves with efficiency coefficients. (int, dot)
        actions = []

        #  Considers whether the player's score will increase
        #  if they place a dot in {dot}.
        #  If the player's score increases,
        #  then the computer can place a dot there to interfere.
        for dot in possible_pos:
            #  Saving the current state.
            save_prev()
            #  Imitation of the player's move.
            self.game.turn += 1
            self.game.turn %= 2
            self.game.put_dot(dot, history_lock=True)
            #  Difference between the player's score before and after simulating their move.
            res = self.game.score[player] - currscore
            #  Loading the current state.
            load_prev()
            #  If the player's score increased,
            #  then the move is recorded in possible actions.
            #  Efficiency coefficient = res * DEFENCE_PRIORITY
            if res > 0:
                actions.append((res * properties.DEFENCE_PRIORITY, dot))

        #  Current score of the computer.
        currscore = self.game.score[computer]

        #  Considers whether the computer's score will increase
        #  if it places a dot in dot.
        #  If the computer's score increases,
        #  then the computer can place a dot there.
        for dot in possible_pos:
            #  Saving the current state.
            save_prev()
            #  Imitation of the player's move.
            self.game.put_dot(dot, history_lock=True)
            #  Difference between the computer's score before and after simulating its move.
            res = self.game.score[computer] - currscore
            #  Loading the current state.
            load_prev()
            #  If the computer's score increased,
            #  then the move is recorded in possible actions.
            #  Efficiency coefficient = res * DEFENCE_PRIORITY
            if res > 0:
                actions.append((res * properties.ATTACK_PRIORITY, dot))

        if not actions:
            #  If no smart moves were found,
            #  then the computer makes a random move.
            return random.choice(possible_pos)
        else:
            #  The computer selects the most efficient move.
            return sorted(actions)[-1][1]
