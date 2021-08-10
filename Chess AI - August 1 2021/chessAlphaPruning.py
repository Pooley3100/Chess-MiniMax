import os

import chess
import random
import pygame
import math
from multiprocessing import Process, Value


def play_chess():
    board = chess.Board()

    print(board.legal_moves)
    print(board)

    while True:
        chess_move = input("Enter chess move: ")
        try:
            board.push_san(chess_move)
            break
        except ValueError:
            print("Please enter a valid move")
            continue

    # Chess Board Turn
    # Random Method (basic)
    # board.push(play_random_ai(board))

    # Move evaluation method (ehh)
    # If no piece can be captured returns to random
    # board.push(play_evaluation_ai(board))

    # Minimax method
    board.push(minimax(board, 3))
    print(board)
    return board


def play_random_ai(board):
    # Returns random move from current legal moves
    move_iter = iter(board.legal_moves)
    move_count = board.legal_moves.count()
    random_move = random.randint(0, move_count)

    # Loop through iterator for the random move choice
    for x in range(random_move + 1):
        move = next(move_iter)
        if x == random_move:
            return move


def play_evaluation_ai(board):
    """
    Evaluation of piece worth then capture

    Requires board piece type of each piece that has attack possible.
    Iterate through moves, any that have attack possible add to list
    use is_capture and piece_at
    """
    eval_list = {}
    move_iter = iter(board.legal_moves)
    for move in move_iter:
        if board.is_capture(move):
            # Add to dict move and value of piece evaluation
            if board.piece_type_at(move.to_square) == chess.PAWN:
                eval_list[move] = 10
            elif board.piece_type_at(move.to_square) == chess.KNIGHT:
                eval_list[move] = 30
            elif board.piece_type_at(move.to_square) == chess.ROOK:
                eval_list[move] = 50
            elif board.piece_type_at(move.to_square) == chess.BISHOP:
                eval_list[move] = 30
            elif board.piece_type_at(move.to_square) == chess.QUEEN:
                eval_list[move] = 90
            elif board.piece_type_at(move.to_square) == chess.KING:
                eval_list[move] = 900

    # Now find highest scoring point
    if len(eval_list) == 0:
        return play_random_ai(board)
    else:
        eval_list_sorted = sorted(eval_list.items(), key=lambda x: x[1], reverse=True)
        return (list(eval_list_sorted)[0])[0]


def minimax(board, searchDepth):
    """
    creates minimax tree
    given a board will create a board for each possible move and each board given a score
    depending on level will decide whether minimise or maximise

    so need to get move list of a board and array of new boards pushing each move to one of
    the boards

    at the same time evaluate each of these moves to find score,
    if no capture then 0 points

    needs a recursive loop depending on searchDepth
    recursive call, is currentDepth equals searchDepth stop
    return best score of current list (2d array, board and score)
    send minimise or max requirement
    find negative of score if it is minimise turn
    only first move need to be remembered

    :param board:
    :param searchDepth:
    :return: move
    """

    # First we have board for each possible move then call recursve minmax
    eval_list = []
    move_iter = iter(board.legal_moves)

    for move in move_iter:
        # Each cell contains board and score
        tempBoard = board.copy(stack=False)
        tempBoard.push(move)
        eval_list.append([tempBoard, evaluation_ai(board, move, 1), move])

    # non alpha pruning
    # for board in eval_list:
    #     # print(board[0].pop().uci())
    #     board[1] += recur_minimax(board[0], searchDepth, 1, 0)

    # same thing but with alpha pruning
    for board in eval_list:
        board[1] += recur_minimax_alphaprune(board[0], searchDepth, 1, 0, -100000, 100000)

    # Now search through scores and pick move with highest value
    move = eval_list[0]
    for board in eval_list:
        if board[1] > move[1]:
            move = board

    winning_move = move[2]
    return winning_move


def recur_minimax(board, searchDepth, currentDepth, minimise):
    # 0 Is minimise, 1 is maximise

    eval_list = []
    score_list = []
    move_iter = iter(board.legal_moves)

    if board.legal_moves.count() == 0:
        return 0

    for move in move_iter:
        # Each cell contains board and score
        tempBoard = board.copy(stack=False)
        tempBoard.push(move)
        eval_list.append([tempBoard, evaluation_ai(board, move, minimise)])

    if currentDepth == searchDepth:
        for board in eval_list:
            score_list.append(board[1])

        if minimise:
            # Wants highest score
            score_list.sort(reverse=True)
        else:
            # Wants Lowest score
            score_list.sort(reverse=False)
        return score_list[0]
    else:
        if minimise == 0:
            minimise = 1
        else:
            minimise = 0

        for board in eval_list:
            board[1] += recur_minimax(board[0], searchDepth, currentDepth + 1, minimise)

    for board in eval_list:
        score_list.append(board[1])

    if minimise:
        score_list.sort(reverse=True)
    else:
        score_list.sort(reverse=False)

    return score_list[0]


def recur_minimax_alphaprune(board, searchDepth, currentDepth, maximise, alpha, beta):
    # 0 Is minimise, 1 is maximise

    eval_list = []
    score_list = []
    move_iter = iter(board.legal_moves)

    if board.legal_moves.count() == 0:
        return 0

    for move in move_iter:
        # Each cell contains board and score
        tempBoard = board.copy(stack=False)
        tempBoard.push(move)
        eval_list.append([tempBoard, evaluation_ai(board, move, maximise)])

    if maximise:
        if currentDepth == searchDepth:
            for board in eval_list:
                score_list.append(board[1])

            score_list.sort(reverse=True)
            return score_list[0]
        else:
            for board in eval_list:
                board[1] += recur_minimax_alphaprune(board[0], searchDepth, currentDepth + 1, 0, alpha, beta)
                alpha = max(alpha, board[1])
                if beta <= alpha:
                    break
    else:
        if currentDepth == searchDepth:
            for board in eval_list:
                score_list.append(board[1])

            score_list.sort(reverse=False)
            return score_list[0]
        else:
            for board in eval_list:
                board[1] += recur_minimax_alphaprune(board[0], searchDepth, currentDepth + 1, 1, alpha, beta)
                beta = min(beta, board[1])
                if beta <= alpha:
                    break

    for board in eval_list:
        score_list.append(board[1])

    if maximise:
        score_list.sort(reverse=True)
    else:
        score_list.sort(reverse=False)

    return score_list[0]


def evaluation_ai(board, move, minimise):
    """
    Evaluate move to give score

    :param minimise:
    :param move:
    :param board:
    :return score:
    """
    score = 0

    if board.is_capture(move):
        # Add to dict move and value of piece evaluation
        if board.piece_type_at(move.to_square) == chess.PAWN:
            score = 10
        elif board.piece_type_at(move.to_square) == chess.KNIGHT:
            score = 30
        elif board.piece_type_at(move.to_square) == chess.ROOK:
            score = 50
        elif board.piece_type_at(move.to_square) == chess.BISHOP:
            score = 30
        elif board.piece_type_at(move.to_square) == chess.QUEEN:
            score = 90
        # elif board.piece_type_at(move.to_square) == chess.KING:
        # score = 900

    # Check for check and checkmate
    tempBoard = board.copy(stack=False)
    tempBoard.push(move)
    if tempBoard.is_check():
        score = 200

    if tempBoard.is_checkmate():
        score = 20000

    # Check if flip score is required
    # - 1 for every extra turn played, this prioritizes checkmate earlier
    if minimise:
        return score - 1
    else:
        return (-score) - 1


def translate_square(square):
    height = math.floor(square/8)
    width = square % 8

    return width * 60, height * 60


def draw_board(board, WIN):
    WIN.fill((255, 255, 255))

    # Create Grid
    DCOLOR = (232, 127, 22)
    LCOLOR = (253, 198, 142)

    COLOR = LCOLOR
    for h in range(0, 8):
        if COLOR == LCOLOR:
            COLOR = DCOLOR
        else:
            COLOR = LCOLOR
        for w in range(0, 8):
            if COLOR == LCOLOR:
                COLOR = DCOLOR
            else:
                COLOR = LCOLOR
            for x in range(60):
                for y in range(60):
                    WIN.set_at((x + (60 * w), (60 * h) + y), COLOR)

    pieces_name = ["Chess_rlt60.png", "Chess_rdt60.png", "Chess_qlt60.png", "Chess_qdt60.png", "Chess_plt60.png",
                   "Chess_pdt60.png", "Chess_nlt60.png", "Chess_ndt60.png", "Chess_klt60.png", "Chess_kdt60.png",
                   "Chess_blt60.png", "Chess_bdt60.png"]

    pieces = []
    for piece in pieces_name:
        pieces.append(pygame.image.load(os.path.join('Assets', piece)))

    # Now to draw pieces
    # White are odd numbers, black even numbers in pieces
    # Get color, then piece type, then position
    for square in range(64):
        piece_odd_or_even = 0
        piece_at = board.piece_type_at(square)

        try:
            if board.piece_at(square).color == chess.WHITE:
                piece_odd_or_even = 1
            elif board.piece_at(square).color == chess.BLACK:
                piece_odd_or_even = 2
        except AttributeError:
            continue

        if piece_at == chess.PAWN:
            pos = translate_square(square)
            WIN.blit(pieces[3 + piece_odd_or_even], pos)
        elif piece_at == chess.ROOK:
            pos = translate_square(square)
            WIN.blit(pieces[-1 + piece_odd_or_even], pos)
        elif piece_at == chess.QUEEN:
            pos = translate_square(square)
            WIN.blit(pieces[1 + piece_odd_or_even], pos)
        elif piece_at == chess.KNIGHT:
            pos = translate_square(square)
            WIN.blit(pieces[5 + piece_odd_or_even], pos)
        elif piece_at == chess.KING:
            pos = translate_square(square)
            WIN.blit(pieces[7 + piece_odd_or_even], pos)
        elif piece_at == chess.BISHOP:
            pos = translate_square(square)
            WIN.blit(pieces[9 + piece_odd_or_even], pos)

    pygame.display.update()


def get_piece(pos):
    # columns 0 to 7
    # rows 0 to 7
    # add 1 to both than times together to get square - 1

    column = math.floor(pos[0]/60)
    row = math.floor(pos[1]/60)

    square = (row*8)+column
    print(square)
    return square


def set_piece(pos, piece):
    goal = get_piece(pos)
    move = chess.Move(piece, goal)
    return move


def is_legal_move(move, board):
    if move in board.legal_moves:
        return True
    else:
        return False


def draw_screen():
    WIDTH, HEIGHT = 480, 480
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess with MiniMax Alpha Pruning")

    board = chess.Board()

    run = True
    piece = None
    move = None
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                piece = get_piece(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONUP:
                move = set_piece(pygame.mouse.get_pos(), piece)
                print(move)
                if is_legal_move(move, board):
                    board.push(move)
                    # Update before min max as this can take a while
                    draw_board(board, WIN)

                    if board.legal_moves.count() == 0:
                        print("Game Over")
                        run = False

                    # Only push minimax once move has been made

                    # p = Process(target=minimax, args=(board, 3))
                    # p.start()
                    # p.join()
                    # board.push()

                    board.push(minimax(board, 3))
                else:
                    print("Not legal Move")

        draw_board(board, WIN)

        if board.legal_moves.count() == 0:
            print("Game Over")
            run = False

    pygame.quit()


if __name__ == '__main__':
    draw_screen()
