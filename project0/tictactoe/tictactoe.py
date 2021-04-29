"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

# the first state in which the board is in
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
    
    # loop throught the cells

    if any(None in row for row in board):
        x = sum(row.count(X) for row in board)
        o = sum(row.count(O) for row in board)

        if x == o:
            return X
        else:
            return O
    else:
        return

# any possible set of actions to run against the player
def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    pActions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                pActions.add((i, j))
    
    return pActions

# the end result of a move or action
def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    i, j = action

    if i < 3 and j < 3 and board[i][j] is EMPTY:
        name = player(board)
        new = copy.deepcopy(board)
        new[i][j] = name

        return new
    
    raise Exception("Invalid Action")

# the winner
def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # every winning move for horizontal
    for mark in [X, O]:
        for row in range(0, 3):
            if all(board[row][col] == mark for col in range(0, 3)):
                return mark
        
        # every winning move for vertical
        for col in range(0, 3):
            if all(board[row][col] == mark for row in range(0, 3)):
                return mark
        
        # every move which can be made diagonally
        diagonals = [[(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]

        for move in diagonals:
            if all(board[row][col] == mark for (row, col) in move):
                return mark
    
    # return None if it is a tie so far
    return None

# is the board terminal???
def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    
    if winner(board) != None:
        return True
    if any(None in row for row in board):
        return False
    return True

# 1 - X else -1 - O or 0 otherwise
def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    
    gWinner = winner(board)

    if gWinner == X:
        return 1
    elif gWinner == O:
        return -1
    else:
        return 0

# the famous minimax algorithm
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if terminal(board):
        return None
    
    if player(board) == X:
        bestVal = -1
        bestMove = (-1, -1)
        a = sum(row.count(EMPTY) for row in board)
        
        if a == 9:
            return bestMove
        
        for action in actions(board):
            moveVal = min_val(result(board, action))
            
            if moveVal == 1:
                bestMove = action
                break

            if moveVal > bestVal:
                bestMove = action
        
        return bestMove
    
    if player(board) == O:
        bestVal = 1
        bestMove = (-1, -1)

        for action in actions(board):
            moveVal = max_val(result(board, action))

            if moveVal == -1:
                bestMove = action
                break

            if moveVal < bestVal:
                bestMove = action
        
        return bestMove


def min_val(board):
    if terminal(board):
        return utility(board)
    
    value = 1

    for action in actions(board):
        value = min(value, max_val(result(board, action)))

        if value == -1:
            break
    
    return value


def max_val(board):
    if terminal(board):
        return utility(board)
    
    value = -1

    for action in actions(board):
        value = max(value, min_val(result(board, action)))
        if value == 1:
            break
    
    return value