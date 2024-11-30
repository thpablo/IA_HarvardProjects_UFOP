"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # The first player is always X
    if board == initial_state():
        print("Estado Inicial: Vez do X")
        return X
    elif terminal(board):
        print("Jogo terminado")
        return None
    else:  # Verify the quanty of O's in the board and return the next player
        countO = sum(row.count(O) for row in board)
        countX = sum(row.count(X) for row in board)

        if countX > countO:
            return O
        else:
            return X

    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    moves = set()
    if terminal(board):
        return moves

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.add((i, j))

    return moves
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
        raise Exception("Invalid action")

    boardCopy = copy.deepcopy(board)
    boardCopy[action[0]][action[1]] = player(board)
    return boardCopy

    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Verify rows
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2]:
            return board[row][0]

    # Verify columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    
    # Verify main diagonal
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    
    # Verify secondary diagonal
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None

    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Verify if there is a winner and end the game
    if winner(board) is not None:
        return True

    # Verify if there is any empty space in the board
    if any(EMPTY in row for row in board) is False:
        return True

    return False
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

    raise NotImplementedError

def min_value(board):
    if terminal(board):
        return utility(board)
    
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

def max_value(board):
    if terminal(board):
        return utility(board)
    
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    # In the X player, try to maximize the value with the best move
    elif player(board) == X:
        points = -math.inf
        for action in actions(board):
            if min_value(result(board, action)) > points:
                points = min_value(result(board, action))
                bestMove = action
        return bestMove 
   
    # In the O player, try to minimize the value with the best move
    elif player(board) == O:
        points = math.inf
        for action in actions(board):
            if max_value(result(board, action)) < points:
                points = max_value(result(board, action))
                bestMove = action
        return bestMove    

    raise NotImplementedError

print(1 % 2)