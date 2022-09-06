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
    Рисует окно и верхнее меню.

    Args:
        size (int, int): Размер окна.
    """
    screen.fill(WHITE)
    pygame.draw.rect(
        screen, UP_MENU,
        [0, 0, size[0], properties.UP_LENGTH])


def draw_polygon(screen, color: tuple, polygon: list):
    """
    Рисует многоугольник.

    Args:
        color: Цвет.
        polygon (list(int, int)): Массив координат точек.
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
    Рисует точку.

    Args:
        color: Цвет.
        pos (int, int): Координаты точки.
    """
    x, y = pos
    xc = properties.GAP + x * properties.BLOCK_SIZE
    yc = properties.UP_LENGTH + properties.GAP + y * properties.BLOCK_SIZE
    pygame.draw.circle(screen, color, [xc, yc], 4)


def draw_vertical_line(screen, color: tuple, x: int, linesY: int):
    """
    Рисует вертикальную линию.

    Args:
        color: Цвет.
        x (int): Координата по OX.
        linesY (int): Количество линий по ОY.
    """
    xb = properties.GAP + x * properties.BLOCK_SIZE
    yb = properties.GAP + properties.UP_LENGTH
    xe = properties.GAP + x * properties.BLOCK_SIZE
    ye = (properties.GAP + properties.BLOCK_SIZE * (linesY - 1) +
          properties.UP_LENGTH)
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_horizontal_line(screen, color: tuple, y: int, linesX: int):
    """
    Рисует горизонтальную линию.

    Args:
        color: Цвет.
        y (int): Координата по OY.
        linesX (int): Количество линий по ОX.
    """
    xb = properties.GAP
    yb = properties.GAP + properties.UP_LENGTH + y * properties.BLOCK_SIZE
    xe = properties.GAP + (linesX - 1) * properties.BLOCK_SIZE
    ye = properties.GAP + properties.UP_LENGTH + y * properties.BLOCK_SIZE
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_text(screen, names, score, linesX, game_mode):
    """
    Рисует текст в верхнем меню.

    Args:
        names (str, str): Имена игроков.
        score (int, int): Счёт игроков.
        linesX (int): Количество линий по ОX.
        game_mode (int): Режим игры.
    """
    k = linesX / 20
    courier = pygame.font.SysFont('courier', int(25 * k))
    text_score_1 = courier.render(f"{names[0]}: {score[0]}", 0, WHITE)
    text_score_2 = courier.render(f"{names[1]}: {score[1]}", 0, WHITE)
    text_mode = courier.render(f"Режим: {game_mode}", 0, WHITE)
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
    Рисует всю игру.

    Args:
        size (tuple): Размер окна.
        pos (tuple): Точка курсора.
        linesX (int): Количество точек по ОХ.
        linesY (int): Количество точек по ОY.
        game_mode (int): Режим игры.
        turn (int): Чей ход.
        dots (list((int, int))): Список активных точек.
        occupied_dots (list((int, int))): Список захваченных точек.
        polygons (list(tuple, list((int, int)))): Список многоугольников
        Цвет и массив точек.
        score (int, int): Счёт игроков.
        names (str, str): Имена игроков.
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
