import pygame
import pygame_menu
import sys
import os
from game import Game
from computer import Computer
import socket


WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

BLUE_PLAYER = 0
RED_PLAYER = 1


def ask_text(ask: str, max_len: int = 10):
    """
    Asks for textual data.

    Args:
        ask (str): Question.

    Returns:
        str: Response.
    """
    screen = pygame.display.set_mode([600, 75], depth=12, vsync=1)
    courier = pygame.font.SysFont('courier', 25)
    clock = pygame.time.Clock()

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
                c = event.unicode
                if c == '\r':
                    return result
                if event.key == pygame.K_BACKSPACE:
                    result = result[:-1]
                else:
                    if len(result) < max_len:
                        result += c

        screen.fill(BLACK)

        dask = courier.render(
            ask, 1, WHITE)
        dresult = courier.render(
            result, 1, WHITE)
        screen.blit(dask, (10, 10))
        screen.blit(dresult, (10, 40))

        pygame.display.flip()
        clock.tick(60)


def ask_binary(ask: str, text1: str, text2: str):
    """
    Choice between 2 options.

    Args:
        ask (str): Question.
        text1 (str): 1st option.
        text2 (str): 2nd option.

    Returns:
        int:
        0 - 1st option
        1 - 2nd option
    """
    screen = pygame.display.set_mode((500, 100), depth=12, vsync=1)
    courier = pygame.font.SysFont('courier', 25)
    clock = pygame.time.Clock()

    box1 = pygame.Rect(20, 40, 140, 32)
    box2 = pygame.Rect(170, 40, 140, 32)

    color1 = WHITE
    color2 = WHITE

    active1 = False
    active2 = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if box1.collidepoint(event.pos):
                    active1 = not active1
                    active2 = False
                elif box2.collidepoint(event.pos):
                    active2 = not active2
                    active1 = False
                else:
                    active1 = False
                    active2 = False
                color1 = GREEN if active1 else WHITE
                color2 = GREEN if active2 else WHITE
            if event.type == pygame.KEYDOWN:
                return 1 if active2 else 0

        screen.fill((30, 30, 30))

        dask = courier.render(ask, True, WHITE)
        dtext1 = courier.render(text1, True, color1)
        dtext2 = courier.render(text2, True, color2)
        screen.blit(dask, (10, 5))
        screen.blit(dtext1, (25, 45))
        screen.blit(dtext2, (175, 45))
        pygame.draw.rect(screen, color1, box1, 2)
        pygame.draw.rect(screen, color2, box2, 2)

        pygame.display.flip()
        clock.tick(60)


def ask_size():
    """
    Requests the field dimensions.
    """
    screen = pygame.display.set_mode((500, 100), depth=12, vsync=1)
    courier = pygame.font.SysFont('courier', 25)
    clock = pygame.time.Clock()

    box1 = pygame.Rect(20, 40, 40, 32)
    box2 = pygame.Rect(70, 40, 40, 32)

    color1 = WHITE
    color2 = WHITE

    active1 = False
    active2 = False

    ask = "Enter the size of the field."
    text1 = ""
    text2 = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if box1.collidepoint(event.pos):
                    active1 = not active1
                    active2 = False
                elif box2.collidepoint(event.pos):
                    active2 = not active2
                    active1 = False
                else:
                    active1 = False
                    active2 = False
                color1 = GREEN if active1 else WHITE
                color2 = GREEN if active2 else WHITE
            if event.type == pygame.KEYDOWN:
                c = event.unicode
                if c == '\r':
                    if not text1:
                        text1 = "39"
                    if not text2:
                        text2 = "32"
                    return int(text1), int(text2)
                if active1:
                    if event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        if len(text1) < 2 and c.isdigit():
                            text1 += c
                if active2:
                    if event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        if len(text2) < 2 and c.isdigit():
                            text2 += c

        screen.fill(BLACK)

        dask = courier.render(ask, True, WHITE)
        dtext1 = courier.render(text1, True, WHITE)
        dtext2 = courier.render(text2, True, WHITE)
        screen.blit(dask, (10, 5))
        screen.blit(dtext1, (25, 45))
        screen.blit(dtext2, (75, 45))
        pygame.draw.rect(screen, color1, box1, 2)
        pygame.draw.rect(screen, color2, box2, 2)

        pygame.display.flip()
        clock.tick(60)


def start_game_in_pvp_mode(x: int, y: int):
    """
    Starts the game in PVP mode.

    Args:
        x (int): Number of points along the X-axis.
        y (int): Number of points along the Y-axis.
    """
    blue_player_name = ask_text("Enter the name of player 1:")
    if not blue_player_name:
        blue_player_name = "Player 1"
    red_player_name = ask_text("Enter the name of player 2:")
    if not red_player_name:
        red_player_name = "Player 2"

    game = Game(
        linesX=x, linesY=y,
        game_mode="PVP",
        names=(blue_player_name, red_player_name))

    score = game.start()

    if score[BLUE_PLAYER] > score[RED_PLAYER]:
        write_record(
            name=blue_player_name,
            score=score[BLUE_PLAYER],
            x=x, y=y)

    if score[RED_PLAYER] > score[BLUE_PLAYER]:
        write_record(
            name=red_player_name,
            score=score[RED_PLAYER],
            x=x, y=y)

    show_result(score, blue_player_name, red_player_name)


def start_game_in_pvc_mode(x: int, y: int):
    """
    Starts game in PVC mode.

    Args:
        x (int): Number of points along the X-axis.
        y (int): Number of points along the Y-axis.
    """
    player_name = ask_text("Enter the name of the player:")
    if not player_name:
        player_name = "Player"

    level = ask_binary("Choose the computer level.", "Weak", "Strong")
    is_computer_first = ask_binary("Who moves first?", "Player", "Computer")

    computer = Computer(level)
    names = (player_name, "Computer")
    if is_computer_first:
        names = names[::-1]
    game = Game(
        linesX=x, linesY=y,
        game_mode="PVC",
        computer=computer, is_computer_first=is_computer_first,
        names=names)
    computer.load_game(game)
    score = game.start()

    if is_computer_first:
        if score[RED_PLAYER] > score[BLUE_PLAYER]:
            write_record(
                name=player_name,
                score=score[RED_PLAYER],
                x=x, y=y)
        show_result(score, "Computer", player_name)
    else:
        if score[BLUE_PLAYER] > score[RED_PLAYER]:
            write_record(
                name=player_name,
                score=score[BLUE_PLAYER],
                x=x, y=y)
        show_result(score, player_name, "Computer")


def start_game_in_sandbox_mode(x: int, y: int):
    """
    Starts game in SANDBOX mode.

    Args:
        x (int): Number of points along the X-axis.
        y (int): Number of points along the Y-axis.
    """
    game = Game(
        linesX=x, linesY=y,
        game_mode="SB")
    score = game.start()
    show_result(score, "Blue", "Red")


def start_game_in_online_mode():
    """
    Starts game in ONLINE mode.

    Args:
        x (int): Number of points along the X-axis.
        y (int): Number of points along the Y-axis.
    """
    type = ask_binary("Choose your role.",
                      "Host",
                      "Player")
    if type == 0:
        ip = socket.gethostbyname(socket.gethostname())
        sock = socket.socket()
        sock.bind((ip, 0))
        ip, port = sock.getsockname()
        show_text(f"ip: {ip} port: {port}")
        sock.listen(1)
        sc, addr = sock.accept()

        name_host = ask_text("Enter the name")
        sc.send(bytes(name_host.encode()))
        show_text("Waiting for the response")
        name_player = str(sc.recv(1024).decode())

        turn = ask_binary("Who moves first?",
                          "Host",
                          "Player")
        sc.send(bytes(str(turn).encode()))

        x, y = ask_size()
        sc.send(bytes(str(x).encode()))
        sc.send(bytes(str(y).encode()))

        game = Game(
            linesX=x, linesY=y,
            game_mode="ONLINE",
            names=(name_host, name_player))
        score = game.start(sc, turn)
        show_result(score, name_host, name_player)
    else:
        sc = socket.socket()
        ip = ask_text("Enter IP of the host", 15)
        port = int(ask_text("Enter port of the host", 5))
        sc.connect((ip, port))

        show_text("Wait for the response")
        name_host = str(sc.recv(1024).decode())
        name_player = ask_text("Enter name")
        sc.send(bytes(name_player.encode()))

        show_text("Wait for the response")
        turn = int(str(sc.recv(1024).decode()))

        x = int(str(sc.recv(1024).decode()))
        y = int(str(sc.recv(1024).decode()))

        game = Game(
            linesX=x, linesY=y,
            game_mode="ONLINE",
            names=(name_player, name_host))
        score = game.start(sc, (turn + 1) % 2)
        show_result(score, name_player, name_host)


def start_game(game_mode):
    match game_mode:
        case "PVP":
            x, y = ask_size()
            start_game_in_pvp_mode(x, y)
        case "PVC":
            x, y = ask_size()
            start_game_in_pvc_mode(x, y)
        case "SB":
            x, y = ask_size()
            start_game_in_sandbox_mode(x, y)
        case "ONLINE":
            start_game_in_online_mode()

    build_menu()


def show_text(text: str):
    """
    Print text

    Args:
        text (str): Text.
    """
    screen = pygame.display.set_mode([500, 40], depth=12, vsync=1)
    courier = pygame.font.SysFont('courier', 25)
    text_1 = courier.render(text, 0, WHITE)
    screen.blit(text_1, (10, 10))
    pygame.display.flip()


def show_result(score: tuple, name_1: str, name_2: str):
    """
    Display results after the game.

    Args:
        score ((int, int)): Score.
        name_1 (str): 1st player name.
        name_2 (str): 2nd player name.
    """
    screen = pygame.display.set_mode([500, 75], depth=12, vsync=1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        courier = pygame.font.SysFont('courier', 25)
        text = f"{name_1}: {score[0]}"
        text_score_1 = courier.render(text, 0, WHITE)
        text = f"{name_2}: {score[1]}"
        text_score_2 = courier.render(text, 0, WHITE)
        text_continue = courier.render("Press any key to continue",
                                       0, WHITE)
        screen.blit(text_score_1, (10, 10))
        screen.blit(text_score_2, (10, 40))
        screen.blit(text_continue, (10, 70))
        pygame.display.flip()


def write_record(name: str, score: int, x: int, y: int):
    """
    Records the result in the record table.

    Args:
        name (str): Winner's name.
        score (int): Winner's score.
        x (int): Number of points along the X-axis.
        y (int): Number of points along the Y-axis.
    """
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
    """
    Displays the record table.
    """
    screen = pygame.display.set_mode([1000, 310], depth=12, vsync=1)
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
            size = f"{r[-2]} by {r[-1][:-1]}"
            text = f"{name} scored {r[-3]} point on the field with {size} size"
            text = courier.render(text, 0, WHITE)
            texts.append(text)
    if len(texts) == 0:
        text = "No records"
        text = courier.render(text, 0, WHITE)
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
    menu = pygame_menu.Menu(
        "Menu", 400, 400,
        theme=pygame_menu.themes.THEME_BLUE)
    menu.add.button('PVP', lambda: start_game("PVP"))
    menu.add.button('PVC', lambda: start_game("PVC"))
    menu.add.button('Online', lambda: start_game("ONLINE"))
    menu.add.button('Record table', show_records)
    menu.add.button('Sandbox', lambda: start_game("SB"))
    menu.add.button('Exit', pygame_menu.events.EXIT)
    menu.set_title("Dots")
    menu.mainloop(screen)


def build_menu():
    pygame.init()
    pygame.display.set_caption("Dots")
    return pygame.display.set_mode([400, 400], depth=12, vsync=1)


if __name__ == "__main__":
    start()
    sys.exit()
