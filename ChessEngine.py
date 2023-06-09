
class GameState:
    """Один из основных классов, в которых отображается состояние фигур на доске"""
    def __init__(self) -> None:
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        self.move_funcs = {'p': self.get_pawn_moves, 'N': self.get_knight_moves, 'B': self.get_bishop_moves,
                           'R': self.get_rook_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.moveLog = []
    
    '''Принимает на вход коорды хода и выполняет его, но не работает с рокировкой, превращением проходной и взятием на проходе'''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move) #добавляем в лог наш ход
        self.whiteToMove = not self.whiteToMove #меняем право следующего хода
    
    '''Отменяет последний ход'''
    def undo_move(self):
        if self.moveLog != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
    
    #ходы с учетом шаха короля соперника
    def get_valid_moves(self):
        return self.get_all_possible_moves()

    #все возможные ходы без учета шаха
    def get_all_possible_moves(self):
        # moves = [Move((6, 4), (4, 4), self.board), Move((1, 3), (2, 3), self.board)]
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                color_turn = self.board[row][col][0] #определяет цвет фигуры ('w' - white, 'b' - black, '-' - empty)
                if (color_turn == 'w' and self.whiteToMove) or (color_turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.move_funcs[piece](row, col, moves)

        return moves

    def get_pawn_moves(self, row, col, moves):
        '''
        Возвращает все возможные ходы для пешки, находящейся на коордах row и col
        '''
        if self.whiteToMove:
            if self.board[row-1][col] == '--': #ход на одну клетку вперед
                moves.append(Move((row, col), (row-1,col), self.board))
                if row == 6 and self.board[row-2][col] == '--': #первый ход на две клетки вперед
                    moves.append(Move((row, col), (row-2,col), self.board))
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == 'b': #слева вражеская фигура
                    moves.append(Move((row, col), (row-1,col-1), self.board))
            if col+1 <= 7:
                if self.board[row-1][col+1][0] == 'b': #справа вражеская фигура
                    moves.append(Move((row, col), (row-1,col+1), self.board))
        
        if not self.whiteToMove:
            if self.board[row+1][col] == '--': #ход на одну клетку вперед
                moves.append(Move((row, col), (row+1,col), self.board))
                if row == 1 and self.board[row+2][col] == '--': #ход на две клетки вперед
                    moves.append(Move((row, col), (row+2,col), self.board))
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == 'w': #слева вражеская фигура
                    moves.append(Move((row, col), (row+1,col-1), self.board))
            if col+1 <= 7:
                if self.board[row+1][col+1][0] == 'w': #справа вражеская фигура
                    moves.append(Move((row, col), (row+1,col+1), self.board))

        return moves

    def get_knight_moves(self, row, col, moves):
        kinght_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in kinght_moves:
            end_row = row + m[0]
            end_col = col + m[1]
            if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # конь не может встать на поле фигуры своего цвета, 
                                               # но может вставть на пустое поле или на поле фигуры вражеского цвета
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        directions = ((-1,-1), (-1,1), (1,-1), (1,1)) #нижний левый угол, нижний правый, верхний левый, верхний правый
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8): #слон может передвигаться максимум через 7 клеток
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:   # вражеская фигура, добавляется в список валид ходов
                        moves.append((Move((row, col), (end_row, end_col), self.board)))
                        break   # не можем "перепрыгнуть" через вражескую фигуру, смотрим в другом направлении
                    else:   # фигура своего цвета, ход не валиден
                        break   # упираемся в фигуру собственного цвета, поэтому смотрим в другом направлении
                else:
                    break

    def get_rook_moves(self, row, col, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1)) #вверх, влево, вниз, вправо
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:   # вражеская фигура, добавляется в список валид ходов
                        moves.append((Move((row, col), (end_row, end_col), self.board)))
                        break   # не можем "перепрыгнуть" через вражескую фигуру, смотрим в другом направлении
                    else:   # фигура своего цвета, ход не валиден
                        break   # упираемся в фигуру собственного цвета, поэтому смотрим в другом направлении
                else:
                    break

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in king_moves:
            end_row = row + m[0]
            end_col = col + m[1]
            if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # король не может встать на поле фигуры своего цвета, 
                                               # но может вставть на пустое поле или на поле фигуры вражеского цвета
                    moves.append(Move((row, col), (end_row, end_col), self.board))





class Move():

    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                     '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                     'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v:k for k, v in files_to_cols.items()}

    def __init__(self, sq_start, sq_end, board):
        self.start_row = sq_start[0]
        self.start_col = sq_start[1]
        self.end_row = sq_end[0]
        self.end_col= sq_end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.moveID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col #уникальное ID каждого хода
        print(self.moveID)

    '''Переопределение оператора равенства (==) для класса Move'''
    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]