import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

CHECKMATE = 1000
STALEMATE = 0


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_best_move(gs, valud_moves):
    turn_multiplayer = 1 if gs.whiteToMove else -1

    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valud_moves)
    for player_move in valud_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponents_moves:
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    print('НАЙДЕН ШАХ И МАТ АААААААААА')
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplayer * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score

                gs.undo_move()

        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move

        gs.undo_move()
    return best_player_move

# def find_best_move_minimax(gs, valid_moves):
#     return


# def find_move_minimax(gs, valid_moves, depth, whiteToMove):
#     global next_move


def score_material(board):
    """
    Считает стоимость фигур на доске. 
    Положительный счет - хорошо для белых, отрицательный - хорошо для черных.
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    
    return score
        