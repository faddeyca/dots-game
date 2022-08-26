import pygame
from properties import Properties as p


up_menu = (0, 177, 205)
red = (255, 0, 0)
red_low = (255, 204, 203)
black = (0, 0, 0)
green = (0, 200, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
blue_low = (173, 216, 230)


def draw_window(screen, size):
    screen.fill(white)
    pygame.draw.rect(screen, up_menu,
                     [0, 0, size[0], p.up_length])


def draw_polygon(screen, color, polygon):
    npolygon = []
    for dot in polygon:
        x = p.gap + dot[0] * p.block_size
        y = p.gap + dot[1] * p.block_size + p.up_length
        npolygon.append((x, y))
    pygame.draw.polygon(screen, color, npolygon)


def draw_dot(screen, color, pos):
    x, y = pos
    xc = p.gap + x * p.block_size
    yc = p.up_length + p.gap + y * p.block_size
    pygame.draw.circle(screen, color, [xc, yc], 4)


def draw_vertical_line(screen, color, x, linesY):
    xb = p.gap + x * p.block_size
    yb = p.gap + p.up_length
    xe = p.gap + x * p.block_size
    ye = p.gap + p.block_size * (linesY - 1) + p.up_length
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_horizontal_line(screen, color, y, linesX):
    xb = p.gap
    yb = p.gap + p.up_length + y * p.block_size
    xe = p.gap + (linesX - 1) * p.block_size
    ye = p.gap + p.up_length + y * p.block_size
    pygame.draw.line(screen, color, [xb, yb], [xe, ye])


def draw_text(screen, score, linesX, mode):
    k = linesX / 20
    courier = pygame.font.SysFont('courier', int(25 * k))
    text_score_1 = courier.render(f"Score 1: {score[0]}", 0, white)
    text_score_2 = courier.render(f"Score 2: {score[1]}", 0, white)
    if mode == 0:
        mode_text = "PVP"
    if mode == 1:
        mode_text = "PVC"
    if mode == 2:
        mode_text = "SB"
    text_mode = courier.render(f"Mode: {mode_text}", 0, white)
    screen.blit(text_score_1, (20, 50))
    screen.blit(text_score_2, (50 + int(300 * k), 50))
    screen.blit(text_mode, (20, 10))


def draw_env(screen, size, linesX, linesY, mode, dots, polygons, score):
    draw_window(screen, size)
    draw_text(screen, score, linesX, mode)

    for polygon, turn in polygons:
        if turn == 0:
            draw_polygon(screen, red_low, polygon)
        else:
            draw_polygon(screen, blue_low, polygon)
    for x in range(linesX):
        draw_vertical_line(screen, black, x, linesY)
    for y in range(linesY):
        draw_horizontal_line(screen, black, y, linesX)
    for dot in dots[0]:
        draw_dot(screen, red, dot)
    for dot in dots[1]:
        draw_dot(screen, blue, dot)
    for dot in dots[2]:
        draw_dot(screen, red, dot)
    for dot in dots[3]:
        draw_dot(screen, blue, dot)
