def print_board(board):
    for line in board:
        print(" | ", end="")
        for row in line:
            print(row, end=" | ")
        print("\n")


def is_game_finished(board):
    if board[0][0] != "-" and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        return board[0][0]
    
    for i in range(len(board)):
        if board[i][0] != "-" and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            return board[i][0]
        
        if board[0][i] != "-" and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
            return board[0][i]

    return None
    



board = [
            ["-", "-", "-"], 
            ["-", "-", "-"], 
            ["-", "-", "-"], 
        ]

# board = [
#             ["X", "X", "X"], 
#             ["-", "-", "-"], 
#             ["-", "-", "-"], 
#         ]

# board = [
#             ["O", "X", "X"], 
#             ["-", "O", "-"], 
#             ["-", "-", "O"], 
#         ]

# board = [
#             ["O", "X", "X"], 
#             ["-", "X", "-"], 
#             ["-", "X", "-"], 
#         ]

# board = [
#             ["O", "X", "X"], 
#             ["O", "-", "-"], 
#             ["O", "-", "-"], 
#         ]

print("Initial Board")
print_board(board)

print("Winner:", is_game_finished(board))