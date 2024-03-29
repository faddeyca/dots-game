import pygame
import properties


UP_MENU = (0, 177, 205)
RED = (255, 0, 0)
LIGHT_RED = (255, 204, 203)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (180, 180, 180)


def draw_window(screen, size: tuple):
    """
    Draws the window and the top menu.

    Args:
        size (int, int): Window size.
    """
    screen.fill(WHITE)
    pygame.draw.rect(
        screen, UP_MENU,
        [0, 0, size[0], properties.UP_LENGTH])


def draw_polygon(screen, color: tuple, polygon: list):
    """
    Draws polygon

    Args:
        color: Color.
        polygon (list(int, int)): Dots coordinates list.
    """
    npolygon = []
    for dot in polygon:
        x = properties.GAP + dot[0] * properties.BLOCK_SIZE
        y = (properties.GAP + dot[1] * properties.BLOCK_SIZE +
             properties.UP_LENGTH)
        npolygon.append((x, y))
    pygame.draw.polygon(screen, color, npolygon)


def draw_dot(screen, color: tuple, pos: tuple):
    """
    Draws dot.

    Args:
        color: Color.
        pos (int, int): Coordinates.
    """
    x, y = pos
    xc = properties.GAP + x * properties.BLOCK_SIZE
    yc = properties.UP_LENGTH + properties.GAP + y * properties.BLOCK_SIZE
    pygame.draw.circle(screen, color, [xc, yc], 4)


def draw_vertical_line(screen, color: tuple, x: int, linesY: int):
    """
    Draws vertical line

    Args:
        color: Color.
        x (int): X-axis coordinate.
        linesY (int): Amount of lines by Y-axis.
    """
    xb = properties.GAP + x * properties.BLOCK_SIZE
    yb = properties.GAP + properties.UP_LENGTH
    xe = properties.GAP + x * properties.BLOCK_SIZE
    ye = (properties.GAP + properties.BLOCK_SIZE * (linesY - 1) +
          properties.UP_LENGTH)
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_horizontal_line(screen, color: tuple, y: int, linesX: int):
    """
    Draws horizontal line.

    Args:
        color: Color.
        y (int): Y-axis coordinate.
        linesX (int): Amount of lines by X-axis.
    """
    xb = properties.GAP
    yb = properties.GAP + properties.UP_LENGTH + y * properties.BLOCK_SIZE
    xe = properties.GAP + (linesX - 1) * properties.BLOCK_SIZE
    ye = properties.GAP + properties.UP_LENGTH + y * properties.BLOCK_SIZE
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_text(screen, names, score, linesX, game_mode):
    """
    Draws text in the top menu.

    Args:
        names (str, str): Names.
        score (int, int): Score.
        linesX (int): Amount of lines by X-axis.
        game_mode (int): Game mode.
    """
    k = linesX / 20
    courier = pygame.font.SysFont('courier', int(25 * k))
    text_score_1 = courier.render(f"{names[0]}: {score[0]}", 0, WHITE)
    text_score_2 = courier.render(f"{names[1]}: {score[1]}", 0, WHITE)
    text_mode = courier.render(f"Mode: {game_mode}", 0, WHITE)
    screen.blit(text_score_1, (20, 50))
    screen.blit(text_score_2, (50 + int(300 * k), 50))
    screen.blit(text_mode, (20, 10))


def draw_env(
    screen,
    size: tuple, pos: tuple,
    linesX: int, linesY: int, game_mode: int,
    turn: int,
    dots: list, occupied_dots: list,
    polygons: list,
    score: tuple,
        names: tuple):
    """
    Draws the whole game.

    Args:
        size (tuple): Window size.
        pos (tuple): Cursor position.
        linesX (int): Number of points along the X-axis.
        linesY (int): Number of points along the Y-axis.
        game_mode (int): Game mode.
        turn (int): Whose turn it is.
        dots (list((int, int))): List of active dots.
        occupied_dots (list((int, int))): List of captured dots.
        polygons (list(tuple, list((int, int)))): List of polygons with color and array of points.
        score (int, int): Players' score.
        names (str, str): Players' names.
    """
    draw_window(screen, size)
    draw_text(screen, names, score, linesX, game_mode)

    for polygon, color in polygons:
        if color == 0:
            draw_polygon(screen, LIGHT_BLUE, polygon)
        else:
            draw_polygon(screen, LIGHT_RED, polygon)

    for x in range(linesX):
        draw_vertical_line(screen, BLACK, x, linesY)
    for y in range(linesY):
        draw_horizontal_line(screen, BLACK, y, linesX)

    if pos is not None:
        if game_mode != "SB":
            if turn == 0:
                draw_dot(screen, LIGHT_BLUE, pos)
            else:
                draw_dot(screen, LIGHT_RED, pos)
        else:
            draw_dot(screen, LIGHT_GRAY, pos)

    blue_dots, red_dots = dots
    for dot in blue_dots:
        draw_dot(screen, BLUE, dot)
    for dot in red_dots:
        draw_dot(screen, RED, dot)

    occupied_blue_dots, occupied_red_dots = occupied_dots
    for dot in occupied_blue_dots:
        draw_dot(screen, BLUE, dot)
    for dot in occupied_red_dots:
        draw_dot(screen, RED, dot)
