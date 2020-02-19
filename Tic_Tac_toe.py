import json
import os
import random
import copy
import sys
from pprint import pprint

def print_board(board):
    print("\n\n")
    for line in board:
        print(" | ", end="")
        for row in line:
            print(row, end=" | ")
        print("\n")


def invert_board(board):
    reverse = copy.deepcopy(board)
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == "X":
               reverse[x][y] = "O" 
            if board[x][y] == "O":
               reverse[x][y] = "X" 
    return reverse


def is_game_finished(board):
    # top-left -> bottom right diag
    if board[0][0] != "-" and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        return board[0][0]
    
    # top-right -> bottom left diag
    if board[0][2] != "-" and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
        return board[0][2]

    # Lines
    for i in range(len(board)):
        if board[i][0] != "-" and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            return board[i][0]
        
        if board[0][i] != "-" and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
            return board[0][i]

    is_tie = True
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == "-":
                is_tie=False
    if is_tie:
        return "DRAW"

    return None
    

def get_possible_moves(board):
    moves = []
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == "-":
                moves.append((x, y))
    return moves


def get_code(board):
    code = ""
    for x in range(len(board)):
        for y in range(len(board[0])):
            code += board[x][y]
    return code


def get_Q_Value(Q_Values, board):
    code = get_code(board)
    
    # Adding new state inside Q_Values
    if code not in Q_Values:
        winner = is_game_finished(board)
        if winner == "X":
            Q_Values.update({code:1.0})
            print("Discovered winning state")
        elif winner == "O":
            Q_Values.update({code:0.0})
            print("Discovered loosing state")
        elif winner == "DRAW":
            print("Discovered DRAW state")
            Q_Values.update({code:0.75})
        else:
            Q_Values.update({code:0.5})
        
    return Q_Values[code]


def update_Q_Value(Q_Values, board, move, is_X, learning_rate):

    test_board = copy.deepcopy(board)

    current_value = get_Q_Value(Q_Values, test_board)
    
    if is_X:
        test_board[move[0]][move[1]] = "X"
    else:
        test_board[move[0]][move[1]] = "O"
    
    new_move_value = get_Q_Value(Q_Values, test_board)
    
    current_code = get_code(board)
    # print("Current: ", Q_Values[current_code])
    variation = learning_rate * (new_move_value - current_value)
    Q_Values[current_code] += variation
    # print("New: ", Q_Values[current_code])
    # print("Variation=", variation, "\n")


def evaluate_move(board, move, Q_Values, is_X=True):
    test_board = copy.deepcopy(board)
    
    if is_X:
        test_board[move[0]][move[1]] = "X"
    else:
        test_board[move[0]][move[1]] = "O"
    
    return get_Q_Value(Q_Values, test_board)


def test_play(initial_board,  Q_Values, nb_matches):
    
    nb_wins = 0
    nb_ties = 0
    nb_losses = 0

    opponent_play_style = "random"
    # opponent_play_style = "self"

    print("Testing against", opponent_play_style, "opponent")

    for nb_iteration in range(nb_matches):
        # Play a full game of tic-tac-toe.
        board = copy.deepcopy(initial_board)
        my_turn = random.randrange(0,10) > 5
        
        while(is_game_finished(board) is None):
            # print_board(board)
            possible_moves = get_possible_moves(board)
            if my_turn:
                # Greedy move
                max_move = possible_moves[0]
                max_value = -1
                for move in possible_moves:
                    value = evaluate_move(board, move, Q_Values, is_X=True)
                    if value > max_value:
                        max_value = value
                        max_move = move
                    
                # Play move
                board[max_move[0]][max_move[1]] = "X"

            else:
                if opponent_play_style == "random":
                    selected_move = possible_moves[random.randint(0, len(possible_moves)-1)]

                    # Play move
                    board[selected_move[0]][selected_move[1]] = "O"
                elif opponent_play_style == "self":
                    # Greedy move
                    max_move = possible_moves[0]
                    max_value = -1
                    for move in possible_moves:
                        value = evaluate_move(invert_board(board), move, Q_Values, is_X=True)
                        if value > max_value:
                            max_value = value
                            max_move = move
                        
                    # Play move
                    board[max_move[0]][max_move[1]] = "O"
                else:
                    raise Exception("Opponent style not implemented:", opponent_play_style)
            my_turn = not my_turn

        winner = is_game_finished(board)
        if winner == "X":
            nb_wins += 1
        elif winner == "DRAW":
            nb_ties += 1
        else:
            nb_losses += 1

    print("Results:")
    print("Wins:", nb_wins / nb_matches)
    print("Losses:", nb_losses / nb_matches)
    print("Ties:", nb_ties / nb_matches)


def train_against_self(initial_board, Q_Values, nb_iterations_total, file_path, reset=False, debug=False):
    
    if reset:
        Q_Values = {}

    print("Training...")
    
    my_turn = random.randrange(0,10) > 5

    epsilon = 0.0
    learning_rate = 0.01

    opponent_play_style = "random"
    # opponent_play_style = "self"
    my_play_style = "e-greedy"
    
    nb_iteration = 0

    for nb_iteration in range(nb_iterations_total):
        # Play a full game of tic-tac-toe.
        board = copy.deepcopy(initial_board)

        # print("Starting new game")
        while(is_game_finished(board) is None):
            if debug:
                print_board(board)
                print("Initial Q_Value=", get_Q_Value(Q_Values, board))
                input("Press key to continue...")
            # print_board(board)
            possible_moves = get_possible_moves(board)
            if my_turn:
                if debug:
                    print("*** X to play ***")
                if random.uniform(0, 1) > epsilon:
                    # Greedy move
                    if debug:
                        print("Greedy move")
                    max_value = -1
                    
                    for move in possible_moves:
                        value = evaluate_move(board, move, Q_Values, is_X=True)
                        if debug:
                            print(move[0], move[1], ":", value)
                        if value > max_value or max_value == -1:
                            max_value = value
                            selected_move = move
                    if debug:
                        print("Selected:", selected_move, "=>", max_value)
                    # Update values
                    update_Q_Value(Q_Values, board, selected_move, True, learning_rate)
                    if debug:
                        print("New Q_Value=", get_Q_Value(Q_Values, board))
                else:
                    # Exploratory move
                    if debug:
                        print("Exploratory move")
                    selected_move = possible_moves[random.randint(0, len(possible_moves)-1)]

                # Play move
                board[selected_move[0]][selected_move[1]] = "X"

            else:
                if debug:
                    print("*** O to play ***")
                if opponent_play_style == "random":
                    possible_moves = get_possible_moves(board)
                    selected_move = possible_moves[random.randint(0, len(possible_moves)-1)]

                    # Update values
                    update_Q_Value(Q_Values, board, selected_move, False, learning_rate)

                    # Play move
                    board[selected_move[0]][selected_move[1]] = "O"
                elif opponent_play_style == "self":
                    max_value = -1
                    for move in possible_moves:
                        value = evaluate_move(invert_board(board), move, Q_Values, is_X=True)
                        if debug:
                            print(move[0], move[1], ":", value)
                        if value > max_value or max_value == -1:
                            max_value = value
                            selected_move = move
                    
                    # Play move
                    board[selected_move[0]][selected_move[1]] = "O"

                else:
                    raise Exception("Opponent style not implemented:", opponent_play_style)
            my_turn = not my_turn

        nb_iteration += 1
        if debug:
            print("Game", nb_iteration, "finished. Victor:", is_game_finished(board))
            print_board(board)

    return Q_Values



board = [
            ["-", "-", "-"], 
            ["-", "-", "-"], 
            ["-", "-", "-"], 
        ]

# board = [
#     ["-", "-", "X"], 
#     ["-", "-", "X"], 
#     ["-", "-", "X"], 
# ]

current_path = os.path.abspath(os.getcwd())
print("Current path = ", current_path)

Q_values_file = "Q_Values_1.json"
file_path = os.path.join(current_path, Q_values_file)
if not os.path.exists(file_path):
    Q_Values = {}
else:
    Q_Values = json.load(open(Q_values_file, "r"))    


print("Q_values:", len(Q_Values))

print("Initial Board")
print_board(board)

if len(sys.argv) > 1 and sys.argv[1] == "evaluate":
    print("Winner:", is_game_finished(board))

if len(sys.argv) > 1 and sys.argv[1] == "reset":
    Q_Values = {}
    json.dump(Q_Values, open(file_path, "w"))

nb_iterations_total = 100000
if len(sys.argv) > 1 and sys.argv[1] == "train_scratch":
    Q_Values = train_against_self(board, Q_Values, nb_iterations_total, file_path, reset=True)
    json.dump(Q_Values, open(file_path, "w"))

if len(sys.argv) > 1 and sys.argv[1] == "train_more":
    Q_Values = train_against_self(board, Q_Values, nb_iterations_total, file_path, reset=False)
    json.dump(Q_Values, open(file_path, "w"))

# print(get_possible_moves(board))
# print("Winner:", is_game_finished(board))

if len(sys.argv) > 1 and sys.argv[1] == "test":
    test_play(board, Q_Values, 10000)

if len(sys.argv) > 1 and sys.argv[1] == "train_debug":
    Q_Values = train_against_self(board, Q_Values, nb_iterations_total, file_path, reset=False, debug=True)