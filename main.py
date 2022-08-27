import pygame
import pygame_menu
import sys
import os

from game import Game

white = (255, 255, 255)


def build_menu():
    '''
    Rebuilds pygame display for menu
    '''
    pygame.init()
    pygame.display.set_caption("Точки")
    return pygame.display.set_mode([400, 400])


def write_record(name, score, x, y):
    if not os.path.exists("records.txt"):
        with open("records.txt", "w", encoding='utf-8') as f:
            a = f"{name} {score} {x} {y}"
            f.write(a)
            f.write("\n")
    else:
        records = []
        with open("records.txt", "r", encoding='utf-8') as f:
            table = f.read().split("\n")
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
    screen = pygame.display.set_mode([1000, 500])
    courier = pygame.font.SysFont('courier', 25)
    texts = []
    if os.path.exists("records.txt"):
        with open("records.txt", "r", encoding='utf-8') as f:
            table = f.read().split("\n")
        for r in table:
            r = r.split(" ")
            if len(r) < 4:
                continue
            text = f"{' '.join(r[:-3])} набрал {r[-3]} очков на поле размера {r[-2]} на {r[-1]}"
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
                return
        count = 0
        for text in texts:
            screen.blit(text, (10, 10 + 30 * count)) 
            count += 1
        pygame.display.flip()


def start_game(mode, player=0):
    size = input_info("Введите размер поля {X Y}")
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
    if mode == 0:
        name_1 = input_info("Введите имя 1 игрока:")
        if len(name_1) == 0:
            name_1 = "Игрок 1"
        name_2 = input_info("Введите имя 2 игрока:")
        if len(name_2) == 0:
            name_2 = "Игрок 2"
        game = Game(x, y, 0, names=(name_1, name_2))
        score = game.start()
        if score[0] > score[1]:
            write_record(name_1, score[0], x, y)
        if score[1] > score[0]:
            write_record(name_2, score[1], x, y)
        show_result(score, mode, player, name_1, name_2)
    if mode == 1:
        name = input_info("Введите имя игрока")
        if len(name) == 0:
            name = "Игрок"
        if player == 0:
            game = Game(x, y, 1, 0, (name, "Компьютер"))
            score = game.start()
            if score[0] > score[1]:
                write_record(name, score[0], x, y)
            show_result(score, mode, player, name_1=name)
        else:
            game = Game(x, y, 1, 1, ("Компьютер", name))
            score = game.start()
            if score[1] > score[0]:
                write_record(name, score[1], x, y)
            show_result(score, mode, player, name_2=name)
    if mode == 2:
        game = Game(x, y, 2)
        score = game.start()
        show_result(score, mode, player, "Синие", "Красные")
    build_menu()


def start():
    '''
    Loads music, initializes menu.
    '''
    screen = build_menu()
    menu = pygame_menu.Menu("Меню", 400, 400,
                            theme=pygame_menu.themes.THEME_BLUE)
    menu.add.button('PVP', lambda: start_game(0))
    menu.add.button('PVC, ходить первым', lambda: start_game(1, 0))
    menu.add.button('PVC, ходить вторым', lambda: start_game(1, 1))
    menu.add.button('Таблица рекордов', show_records)
    menu.add.button('Песочница', lambda: start_game(2))
    menu.add.button('Выход', pygame_menu.events.EXIT)
    menu.set_title("Точки")
    menu.mainloop(screen)


def input_info(input_text):
    timer = pygame.time.Clock()
    screen = pygame.display.set_mode([400, 75])
    name = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if len(name) != 0:
                    return name
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    return name
                if event.key == pygame.K_BACKSPACE:
                    if len(name) != 0:
                        screen.fill((0, 0, 0))
                        name = name[:-1]
                else:
                    if len(name) < 10:
                        c = event.unicode
                        if c == '\r':
                            return name
                        name += c
        courier = pygame.font.SysFont('courier', 25)
        text = courier.render(input_text,
                              1, white)
        text_continue = courier.render(name,
                                       1, white)
        screen.blit(text, (10, 10))                               
        screen.blit(text_continue, (10, 40))
        timer.tick(60)
        pygame.display.flip()


def show_result(score, mode, player, name_1=None, name_2=None):
    '''
    Shows score in the end
    '''
    screen = pygame.display.set_mode([500, 75])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        courier = pygame.font.SysFont('courier', 25)
        if mode != 1:
            text_score_1 = courier.render(f"{name_1}: {score[0]}", 0, white)
            text_score_2 = courier.render(f"{name_2}: {score[1]}", 0, white)
        else:
            if player == 0:
                text_score_1 = courier.render(f"{name_1}: {score[0]}", 0, white)
                text_score_2 = courier.render(f"Computer: {score[1]}", 0, white)
            else:
                text_score_1 = courier.render(f"Computer: {score[0]}", 0, white)
                text_score_2 = courier.render(f"{name_2}: {score[1]}", 0, white)
        text_continue = courier.render("Press any key to continue",
                                       0, white)
        screen.blit(text_score_1, (10, 10))
        screen.blit(text_score_2, (10, 40))
        screen.blit(text_continue, (10, 70))
        pygame.display.flip()


if __name__ == "__main__":
    start()
    sys.exit()
