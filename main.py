import pygame
import pygame_menu
import sys
import os
from game import Game
from computer import Computer


white = (255, 255, 255)

PVP = 0
PVC = 1
SANDBOX = 2

BLUE_PLAYER = 0
RED_PLAYER = 1


def input_text(show_text):
    screen = pygame.display.set_mode([600, 75])
    result = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if len(result) != 0:
                    return result
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    return result
                if event.key == pygame.K_BACKSPACE:
                    if len(result) != 0:
                        screen.fill((0, 0, 0))
                        result = result[:-1]
                else:
                    if len(result) < 10:
                        c = event.unicode
                        if c == '\r':
                            return result
                        result += c
        courier = pygame.font.SysFont('courier', 25)
        text = courier.render(show_text,
                              1, white)
        text_continue = courier.render(result,
                                       1, white)
        screen.blit(text, (10, 10))
        screen.blit(text_continue, (10, 40))
        pygame.display.flip()


def start_game_in_pvp_mode(x, y):
    blue_player_name = input_text("Введите имя 1 игрока:")
    if not blue_player_name:
        blue_player_name = "Игрок 1"
    red_player_name = input_text("Введите имя 2 игрока:")
    if not red_player_name:
        red_player_name = "Игрок 2"

    game = Game(linesX=x, linesY=y,
                game_mode=PVP,
                names=(blue_player_name, red_player_name))

    score = game.start()

    if score[BLUE_PLAYER] > score[RED_PLAYER]:
        write_record(name=blue_player_name,
                     score=score[BLUE_PLAYER],
                     x=x, y=y)

    if score[RED_PLAYER] > score[BLUE_PLAYER]:
        write_record(name=red_player_name,
                     score=score[RED_PLAYER],
                     x=x, y=y)

    show_result(score, blue_player_name, red_player_name)


def start_game_in_pvc_mode(x, y):
    player_name = input_text("Введите имя игрока:")
    if not player_name:
        player_name = "Игрок"

    level = input_text("Введите сложность компьютера: {0 или 1}")
    try:
        level = int(level)
    except ValueError:
        level = 0
    level = min(1, level)
    level = max(0, level)

    is_computer_first = input_text("Кто ходит первый? {0 или 1}")
    try:
        is_computer_first = int(is_computer_first)
    except ValueError:
        is_computer_first = 0
    is_computer_first = min(1, is_computer_first)
    is_computer_first = max(0, is_computer_first)

    computer = Computer(level)
    names = (player_name, "Computer")
    if is_computer_first:
        names = names[::-1]
    game = Game(linesX=x, linesY=y,
                game_mode=PVC,
                computer=computer, is_computer_first=is_computer_first,
                names=names)
    computer.load_game(game)
    score = game.start()

    if is_computer_first:
        if score[RED_PLAYER] > score[BLUE_PLAYER]:
            write_record(name=player_name,
                         score=score[RED_PLAYER],
                         x=x, y=y)
        show_result(score, "Computer", player_name)
    else:
        if score[BLUE_PLAYER] > score[RED_PLAYER]:
            write_record(name=player_name,
                         score=score[BLUE_PLAYER],
                         x=x, y=y)
        show_result(score, player_name, "Computer")


def start_game_in_sandbox_mode(x, y):
    game = Game(linesX=x, linesY=y,
                game_mode=SANDBOX)
    score = game.start()
    show_result(score, "Синие", "Красные")


def get_field_size():
    size = input_text("Введите размер поля {X Y}")
    try:
        size = size.split(" ")
        x = int(size[0])
        y = int(size[1])
    except IndexError:
        x = 39
        y = 32
    except ValueError:
        x = 39
        y = 32
    return x, y


def start_game(game_mode):
    x, y = get_field_size()

    if game_mode == PVP:
        start_game_in_pvp_mode(x, y)
    if game_mode == PVC:
        start_game_in_pvc_mode(x, y)
    if game_mode == SANDBOX:
        start_game_in_sandbox_mode(x, y)

    build_menu()


def show_result(score, name_1=None, name_2=None):
    screen = pygame.display.set_mode([500, 75])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        courier = pygame.font.SysFont('courier', 25)
        text = f"{name_1}: {score[0]}"
        text_score_1 = courier.render(text, 0, white)
        text = f"{name_2}: {score[1]}"
        text_score_2 = courier.render(text, 0, white)
        text_continue = courier.render("Press any key to continue",
                                       0, white)
        screen.blit(text_score_1, (10, 10))
        screen.blit(text_score_2, (10, 40))
        screen.blit(text_continue, (10, 70))
        pygame.display.flip()


def write_record(name, score, x, y):
    if not os.path.exists("records.txt"):
        with open("records.txt", "w", encoding='utf-8') as f:
            a = f"{name} {score} {x} {y}"
            f.write(a)
            f.write("\n")
    else:
        records = []
        with open("records.txt", "r", encoding='utf-8') as f:
            table = f.readlines()
        for r in table:
            rr = r.split(" ")[-3:]
            if len(rr) < 3:
                continue
            val = 1000 / (int(rr[0]) * int(rr[1]) * int(rr[2]))
            records.append((val, r))
        records.append((1000 / (score * x * y), f"{name} {score} {x} {y}"))
        with open("records.txt", "w", encoding='utf-8') as f:
            for record in sorted(records):
                f.write(record[1])
                f.write("\n")


def show_records():
    screen = pygame.display.set_mode([1000, 310])
    courier = pygame.font.SysFont('courier', 25)
    texts = []
    if os.path.exists("records.txt"):
        with open("records.txt", "r", encoding='utf-8') as f:
            table = f.readlines()
        for r in table:
            r = r.split(" ")
            if len(r) < 4:
                continue
            name = ' '.join(r[:-3])
            size = f"{r[-2]} на {r[-1][:-1]}"
            text = f"{name} набрал {r[-3]} очков на поле размера {size}"
            text = courier.render(text, 0, white)
            texts.append(text)
    if len(texts) == 0:
        text = "Нет записей"
        text = courier.render(text, 0, white)
        texts.append(text)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                build_menu()
                return
        count = 0
        for text in texts:
            screen.blit(text, (10, 10 + 30 * count))
            count += 1
        pygame.display.flip()


def start():
    screen = build_menu()
    menu = pygame_menu.Menu("Меню", 400, 400,
                            theme=pygame_menu.themes.THEME_BLUE)
    menu.add.button('PVP', lambda: start_game(PVP))
    menu.add.button('PVC', lambda: start_game(PVC))
    menu.add.button('Таблица рекордов', show_records)
    menu.add.button('Песочница', lambda: start_game(SANDBOX))
    menu.add.button('Выход', pygame_menu.events.EXIT)
    menu.set_title("Точки")
    menu.mainloop(screen)


def build_menu():
    pygame.init()
    pygame.display.set_caption("Точки")
    return pygame.display.set_mode([400, 400])


if __name__ == "__main__":
    start()
    sys.exit()
