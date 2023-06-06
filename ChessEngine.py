
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
        moves = [Move((6, 4), (4, 4), self.board)]
        print('list: ', moves[0].moveID)
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                color_turn = self.board[row][col][0] #определяет цвет фигуры ('w' - white, 'b' - black, '-' - empty)
                if (color_turn == 'w' and self.whiteToMove) and (color_turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.get_pawn_moves(row, col, moves)
                    if piece == '':
                        self.get_rook_moves(row, col, moves)

        return moves

    def get_pawn_moves(self, row, col, moves):
        pass

    def get_rook_moves(self, row, col, moves):
        pass





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