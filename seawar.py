from random import randint, choice
from PIL import Image, ImageDraw

near_list = [(0, -1), (0, 1), (1, 0), (-1, 0)]
all_near_list = [(0, -1), (0, 1), (1, 0), (-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
diag_near_list=[(-1, -1), (-1, 1), (1, -1), (1, 1)]

bot_memory = []


def generate_white_board():
    board = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']]

    return board


#  x это HORIZONTAL(цифры на настоящей доске для морского боя)
#  y это VERTICAL(буквы на настоящей доске для морского боя)


def generate_board():
    def check_horizont(start, stop, y):
        if start - 1 >= 0:
            start -= 1
        if stop + 1 <= 9:
            stop += 1

        for ind in range(start, stop):
            if board[y][ind] == '1':
                return False

        if y - 1 >= 0:
            for ind in range(start, stop):
                if board[y - 1][ind] == '1':
                    return False

        if y + 1 <= 9:
            for ind in range(start, stop):
                if board[y + 1][ind] == '1':
                    return False

        return True

    def check_vertical(start, stop, x):
        if start - 1 >= 0:
            start -= 1
        if stop + 1 <= 9:
            stop += 1

        for ind in range(start, stop):
            if board[ind][x] == '1':
                return False

        if x - 1 >= 0:
            for ind in range(start, stop):
                if board[ind][x - 1] == '1':
                    return False

        if x + 1 <= 9:
            for ind in range(start, stop):
                if board[ind][x + 1] == '1':
                    return False

        return True

    board = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']]
    ships_list = [(4, 1), (3, 2), (2, 3)]
    for size, quantity in ships_list:
        for qwer in range(quantity):
            placed = False
            while not placed:
                x, y = randint(0, 9), randint(0, 9)
                direction = choice(["h", "v"])
                if direction == "h":
                    if x + size >= 10:
                        continue
                    elif check_horizont(x, x + size, y):
                        placed = True
                        for ind in range(x, x + size):
                            board[y][ind] = '1'
                elif direction == "v":
                    if y + size >= 10:
                        continue
                    elif check_vertical(y, y + size, x):
                        placed = True
                        for ind in range(y, y + size):
                            board[ind][x] = '1'
    for _ in range(4):
        placed = False
        while not placed:
            fl = True
            x, y = randint(0, 9), randint(0, 9)
            for koef in all_near_list:
                if 0 <= x + koef[0] <= 9 and 0 <= y + koef[1] <= 9 and board[x + koef[0]][y + koef[1]] != '0':
                    fl = False
            if board[x][y] != '0':
                fl = False

            if fl:
                placed = True
                board[x][y] = '1'

    return board


def print_board(board):
    for i in board:
        print(' '.join(i))
    print()


def display_board(board, board_shoot, board_bot, empty_board, fill_board):
    image_field = Image.open(empty_board)
    img = image_field
    draw = ImageDraw.Draw(img)
    for i in range(10):
        for j in range(10):
            if board[i][j] == '1':
                draw.rectangle((36 + j * 38, 33 + i * 38, 70 + j * 38, 67 + i * 38), fill="blue", outline="blue")
            elif board[i][j] == '*':
                draw.rectangle((36 + j * 38, 33 + i * 38, 70 + j * 38, 67 + i * 38), fill="grey", outline="grey")
            elif board[i][j] == '#':
                draw.rectangle((36 + j * 38, 33 + i * 38, 70 + j * 38, 67 + i * 38), fill="blue", outline="blue")
                draw.line(xy=(
                                (37 + j * 38, 34 + i * 38),
                                (68 + j * 38, 65 + i * 38),
                                            ), fill="red", width=6)
                draw.line(xy=(
                                (68 + j * 38, 35 + i * 38),
                                (37 + j * 38, 66 + i * 38),
                                            ), fill="red", width=6)
            if board_shoot[i][j] == '#':
                draw.rectangle((500 + j * 38, 32 + i * 38, 534 + j * 38, 66 + i * 38), fill="blue", outline="blue")
                draw.line(xy=(
                                (501 + j * 38, 33 + i * 38),
                                (532 + j * 38, 64 + i * 38),
                                            ), fill="red", width=6)
                draw.line(xy=(
                                (532 + j * 38, 34 + i * 38),
                                (501 + j * 38, 65 + i * 38),
                                            ), fill="red", width=6)
            if board_shoot[i][j] == '*':
                draw.rectangle((500 + j * 38, 32 + i * 38, 534 + j * 38, 66 + i * 38), fill="grey", outline="grey")
    img.thumbnail(size=(776, 344))
    img.save(fill_board, "PNG")


def game_over(board):
    for i in board:
        if '1' in i:
            return False
    return True


def ship_is_alive(x, y, board):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if 0 <= i <= 9 and 0 <= j <= 9:
                if board[i][j] == '1':
                    return True
    return False


def mark_ship(board):
    for i in range(10):
        for j in range(10):
            if board[i][j]=='#':
                for koef in all_near_list:
                    if 0 <= i + koef[0] <= 9 and 0 <= j + koef[1] <= 9 and board[i + koef[0]][j + koef[1]]!='#':
                        board[i + koef[0]][j + koef[1]]='*'


def shoot(x, y, board, reaction_board):
    if board[x][y] == '0':
        board[x][y] = '*'
        reaction_board[x][y] = '*'
        return 'Мимо'
    elif board[x][y] == '1':
        board[x][y] = '#'
        reaction_board[x][y] = '#'
        if ship_is_alive(x, y, board):
            return 'Попал'
        else:
            mark_ship(reaction_board)
            return 'Уничтожил!'
    elif board[x][y] in ['*', '#']:
        return 'Туда уже стреляли'


def bot_shoot(board, reaction_board):
    mess = []
    global bot_memory
    if len(bot_memory) == 0:
        shoot_list = []
        for i in range(10):
            for j in range(10):
                if board[i][j] == '0':
                    shoot_list.append([i, j])
        indx = randint(0, len(shoot_list))
        x, y = shoot_list[indx]
        del shoot_list[indx]
        res = shoot(x, y, board, reaction_board)
        mess.append(res)
        while res == 'Попал':
            bot_memory.append((x, y))
            for koef in near_list:
                if (x + koef[0], y + koef[1]) in shoot_list and board[x + koef[0]][y + koef[1]] == '0':
                    x, y = x + koef[0], y + koef[1]
                    res = shoot(x, y, board, reaction_board)
                    break
            if res == 'Уничтожил!':
                bot_memory = []
                bot_shoot(board, reaction_board)
            mess.append(res)
    else:
        shoot_list = []
        for i in range(10):
            for j in range(10):
                if board[i][j] == '0':
                    shoot_list.append([i, j])
        x, y = bot_memory[-1]
        while (x, y) == bot_memory[-1]:
            res = None
            for koef in near_list:
                if (x + koef[0], y + koef[1]) in shoot_list and board[x + koef[0]][y + koef[1]] == '0':
                    x, y = x + koef[0], y + koef[1]
                    res = shoot(x, y, board, reaction_board)
                    break
            if res == 'Уничтожил!':
                bot_memory = []
                bot_shoot(board, reaction_board)
            elif res == 'Попал':
                bot_memory.append((x, y))
            mess.append(res)
    return mess


def create_legal_moves(player_board_shoot):
    legal_moves = [[]]
    for i in range(10):
        for j in range(10):
            if player_board_shoot[i][j] == '0':
                legal_moves.append([i, j])
    return legal_moves