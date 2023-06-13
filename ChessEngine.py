
class GameState:
    """
    Основной класс, отвечающий за расположение фигур на доске и 
    за правила шахмат, согласно которым можно делать тот или иной ход.

    Методы:
    ------
    |make_move(self, Move)
        Получает экземпляр класса Move и совершает ход на доске, изменяя список self.board
    |undo_move(self)
        Отменяет последний сделанный ход
    |get_valid_moves(self)
        Возвращает список айдишников всех валидных ходов (в частности тех ходов, когда король находится под шахом), 
        работает совместно с методом get_all_possible_moves() и check_for_pins_and_checks()
    |get_all_possible_moves(self)
        Возвращает список айдишников всех ВОЗМОЖНЫХ ходов по правилам движения фигур 
        (в том числе невозможных, например когда пешка связана слоном
        и она идет вперед, тем самым подставляя короля под шах, что невозможно). get_valid_moves() отсеивает эти ходы,
        полученные из метода get_all_possible_moves()
    |get_pawn_moves(self, row, col, moves), get_knight_moves(self, row, col, moves), get_bishop_moves(...), etc
        Получает на вход координаты фигуры и добавляет в список moves ходы, согласно которым ходит та или иная фигура
        Также содержит в себе механизм связок (немного грязный из-за своего копипастности)
    TODO: Дописать документацию


    """
    str 
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
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = () #координаты клеток в которых возможно взятие на проходе
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    
    '''Принимает на вход коорды хода и выполняет его, но не работает с рокировкой, превращением проходной и взятием на проходе'''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move) #добавляем в лог наш ход
        self.whiteToMove = not self.whiteToMove #меняем право следующего хода
        #обновляем положение короля если он двигался
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        if move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        #проходная пешка
        if move.pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'
        
        #взятие на проходе
        if move.enpassant_move:
            self.board[move.start_row][move.end_col] = '--' #взятие пешки
        #обновление значения переменной enpassant_move
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: #только для хода пешки на 2 клетки вперед
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.end_col)
        else:
            self.enpassant_possible = ()
        
        # ходы с рокировкой
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # рокировка на королевский фланг
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # переносим ладью на новую клетку
                self.board[move.end_row][move.end_col + 1] = '--'  # стираем старую ладью
            else:  # рокировка на ферзевый фланг
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # переносим ладью на новую клетку
                self.board[move.end_row][move.end_col - 2] = '--'  # стираем старую ладью
        
        #обновление прав на рокировку - когда ход совершен королем или ладьей
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                  self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    
    '''Отменяет последний ход'''
    def undo_move(self):
        if self.moveLog != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
        if move.piece_moved == 'wK':
            self.white_king_location = (move.start_row, move.start_col)
        if move.piece_moved == 'bK':
            self.black_king_location = (move.start_row, move.start_col)

        #отменить ход взятия на проходе
        if move.enpassant_move:
            self.board[move.end_row][move.end_col] = '--'
            self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possible = (move.end_row, move.end_col)
        #возврат возможности ходит пешке на 2 клетке вперед
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ()

        #возврат прав на рокировку
        self.castle_rights_log.pop() #удаляем новые права на рокировку удалением последнего элемента из списка
        self.current_castling_rights = self.castle_rights_log[-1] #возвращаем старые права

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # королевская сторона
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = '--'
            else:  # ферзевая сторона
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
        self.checkmate = False
        self.stalemate = False
    
    #Обновление прав на рокировку
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0: #левая ладья
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7: #правая ладья
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0: #левая ладья
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7: #правая ладья
                    self.current_castling_rights.bks = False


    
    #ходы с учетом шаха короля 
    def get_valid_moves(self):
        # temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        if not self.whiteToMove:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.inCheck:
            if len(self.checks) == 1: # только 1 шах, можно передвинуть короля или защитить его своей фигурой
                moves = self.get_all_possible_moves()
                check = self.checks[0] 
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #вражеская фигура, которая дает шах
                valid_squares = [] # клетки, на которые фигуры могут ходить в случае шаха
                #Если шах дал конь, то можно либо забрать его либо отойти, все остальные шахующие фигуры можно заблочить
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1,8): #(!!) этот цикл генерирует коорды клеток куда в теории можно поставить фигуру для блокировки шаха
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) #check[2] и check[2] это направления (d) шаха
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #при достижения коордов шахующей фигуры
                            break
                # print(check)
                print(king_row, king_col)
                print('VALID SQ:', valid_squares)
                #удаление всех ходов, не предотвращающих шах
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].piece_moved[1] != 'K': #ход не двигает короля, значит он должен либо защитить его, либо забрать шахующую фигуру
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: #ход не защищает от шаха
                            moves.remove(moves[i])
                
            else: #двойной шах, единственный валид ходы - движение короля
                self.get_king_moves(king_row, king_col, moves)
        else: #шаха нет, значит все возможные ходы имеют право быть (кроме хода связаных фигур)
            moves = self.get_all_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
                print("ШАХ И МАТ")
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        # self.enpassant_possible = temp_enpassant_possible
        self.current_castling_rights = temp_castle_rights
        return moves

    def square_under_attack(self, row, col):
            """
            Определяем является ли клетка под атакой вражеской фигуры
            """
            self.whiteToMove = not self.whiteToMove  # меняем право хода 
            opponents_moves = self.get_all_possible_moves()
            self.whiteToMove = not self.whiteToMove # меняем право хода обратно
            for move in opponents_moves:
                if move.end_row == row and move.end_col == col:  # клетка находится под атакой
                    return True
            return False
    
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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[row-1][col] == '--': #ход на одну клетку вперед
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row-1,col), self.board))
                    if row == 6 and self.board[row-2][col] == '--': #проверка связанности фигуры
                        moves.append(Move((row, col), (row-2,col), self.board))

            #взятия пешкой
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == 'b': #слева вражеская фигура
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board, enpassant_move=True))
                                     
            if col+1 <= 7:
                if self.board[row-1][col+1][0] == 'b': #справа вражеская фигура
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row-1,col+1), self.board))
                elif (row-1, col+1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row-1, col+1), self.board, enpassant_move=True))
        
        if not self.whiteToMove: #черные пешки
            if self.board[row+1][col] == '--': #ход на одну клетку вперед
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row+1,col), self.board))
                    if row == 1 and self.board[row+2][col] == '--': #ход на две клетки вперед
                        moves.append(Move((row, col), (row+2,col), self.board))
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == 'w': #слева вражеская фигура
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row+1,col-1), self.board))
                elif (row+1, col-1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row+1, col-1), self.board, enpassant_move=True))
                                     
            if col+1 <= 7:
                if self.board[row+1][col+1][0] == 'w': #справа вражеская фигура
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row+1,col+1), self.board))
                elif (row+1, col+1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row+1, col+1), self.board, enpassant_move=True))
                                     

        # return moves

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        kinght_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in kinght_moves:
            end_row = row + m[0]
            end_col = col + m[1]
            if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                # если конь связан диагонально, то эту фигуру невозможно забрать конем. Аналогично и с ортогоналями.
                # поэтому при работе со связкой коня нет смысла рассматривать направление связки, в отличии от остальных фигур.
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color: # конь не может встать на поле фигуры своего цвета, 
                                                # но может вставть на пустое поле или на поле фигуры вражеского цвета
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (-1,1), (1,-1), (1,1)) #нижний левый угол, нижний правый, верхний левый, верхний правый
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8): #слон может передвигаться максимум через 7 клеток
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # т.к. ферзь по сути получает ходы из функций get_rook_moves и get_bishop_moves,
                # то для него мы рассматриваем ситуацию связки отдельно, а здесь мы работаем только со связками ладьи
                if self.board[row][col][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0,-1), (1,0), (0,1)) #вверх, влево, вниз, вправо
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
        # king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: #король не может встать на поле фигуры своего цвета, 
                    if ally_color == 'w':
                        # временное расположение короля на клетку (end_row, end_col) для последующей проверки его шахов на этой клетке
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    inCheck, pins, checks = self.check_for_pins_and_checks()
                    if not inCheck:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

                    if ally_color == 'w':
                        # возвращение короля после проверки шаха в оригинальное положение обратно
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def get_castle_moves(self, row, col, moves):
        """
        Генерирует все валидных рокировки для короля с коордами (row, col) и добавляет их в список ходов
        """
        if self.square_under_attack(row, col):
            return  # рокировка под шахом невозможна
        if (self.whiteToMove and self.current_castling_rights.wks) or (
                not self.whiteToMove and self.current_castling_rights.bks):
            self.get_king_side_castle_moves(row, col, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (
                not self.whiteToMove and self.current_castling_rights.bqs):
            self.get_queen_side_castle_moves(row, col, moves)

    def get_king_side_castle_moves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))
        
        

    def check_for_pins_and_checks(self):
        pins = [] # клетки где находятся связанные фигуры своего цвета и направление откуда они связаны
        checks = [] # клетки где вражеская фигура угрожает шахом
        inCheck = False
        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # проверка на связки и шахи с перспективы короля, отслеживаем связи
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == (): # наша первая фигура в направлении d потенциально может быть связана
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:       # если же есть наша вторая фигура в этом же направлении d то здесь не может быть связки,
                            break   # и мы переходим к следующей итерации и смотрим уже в другом направлении d`

                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 возможных ситуаций если в направлении d находится вражеская фигура:
                        # 1) на одной ортогонали с королем находится вражеская ладья
                        # 2) на одной диагонали с королем находится вражеский слон
                        # 3) на диагонали соседней верхней левой или правой клетки относительно короля находится вражеская пешка
                        # 4) в любом возможном направлении с королем находится вражеский ферзь
                        # 5) любое направление в 1 клетку от короля находится вражеский король (предотвращение возможности
                        #    ходить королем на клетки, которые контролирует вражеский король)
                        if (0 <= j <= 3 and piece_type == 'R') or \
                            (4<= j <= 7 and piece_type == 'B') or \
                            (i == 1 and piece_type == 'p' and ((enemy_color == 'w' and 6<=j<=7) or (enemy_color == 'b' and 4<=j<=5))) or \
                            (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possible_pin == (): #в направлении не было собственных прикрывающих (связанных) фигур, поэтому это шах
                                inCheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: #фигура прикрывает короля, поэтому она связана
                                pins.append(possible_pin)
                                break
                        else: #вражеская фигура не представляет угрозы шаха => связанных фигур также нет
                            break
                else:
                    break 

        #проверка на шахи вражеского коня
        kinght_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in kinght_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0<= end_row < 8 and 0 <= end_col < 8: # чтобы не выйти за границы доски
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': #вражеский конь атакует короля
                    inCheck = True
                    checks.append((end_row, end_col, m[0], m[1]))
        # print('WHITE TO MOVE: ', self.whiteToMove)
        # print('INCHECK: ', inCheck)
        return inCheck, pins, checks

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs) -> None:
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                     '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                     'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v:k for k, v in files_to_cols.items()}

    def __init__(self, sq_start, sq_end, board, enpassant_move = False, is_castle_move=False):
        self.start_row = sq_start[0]
        self.start_col = sq_start[1]
        self.end_row = sq_end[0]
        self.end_col= sq_end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        #прозодные пешки
        self.pawn_promotion = False
        self.promotion_choice = 'Q'
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.pawn_promotion = True
        #взятие на проходе
        self.enpassant_move = enpassant_move
        if self.enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
        
        self.is_castle_move = is_castle_move

        self.moveID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col #уникальное ID каждого хода

    '''Переопределение оператора равенства (==) для класса Move'''
    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]