import ChessEngine
import pygame as p

WIDTH = HEIGHT = 512+256
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    """Загружает изображения фигур и подгоняет их под размер доски"""
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f'images/{piece}.png'), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill('white')
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_was_made = False #флаговая переменная для обозначения того, был ли сделан ход

    load_images()
    running = True
    sq_selected = () #выбранный квадрат доски, на которую кликнул юзер (координаты a-h, 1-8)
    player_clicks = [] #содержит в себе 2 квадрата доски на которую кликнул юзер (2 списка из коррдинат первого клика и коорд второго клика)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sq_selected == (row, col): #юзер дважды кликает на один и тот же квадрат доски
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    # print(move.get_chess_notation())
                    if move in valid_moves:
                        gs.make_move(move)
                        move_was_made = True
                        sq_selected = () #сбрасываем клики юзера
                        player_clicks = []
                    else:
                        player_clicks = [sq_selected]
            
            elif e.type == p.KEYDOWN: 
                if e.key == p.K_z: #клавиша 'z' для отмены последнего хода
                    gs.undo_move()
                    move_was_made = True

        if move_was_made:
            print("LEN VALID MOVES: ", len(valid_moves))
            valid_moves = gs.get_valid_moves()
            move_was_made = False

        draw_game_state(screen, gs)

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs):
    """Рисует всю графику для шахмат"""
    draw_board(screen)

    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [p.Color('white'), p.Color('grey')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()