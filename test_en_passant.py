import ChessEngine

# Set up a position for en passant
gs = ChessEngine.GameState()

# Clear the board
gs.board = [
    ["--"] * 8 for _ in range(8)
]

# Place white pawn on e5 (row 3, col 4)
gs.board[3][4] = "wp"

# Place black pawn on d7 (row 1, col 3)
gs.board[1][3] = "bp"

# White to move
gs.whiteToMove = True

print("Board setup:")
for row in gs.board:
    print(row)

# Make black pawn move d7 to d5 (row 1 to 3, col 3)
move_black = ChessEngine.Move((1, 3), (3, 3), gs.board)
gs.makeMove(move_black)
gs.whiteToMove = True  # Switch back to white's turn for testing

print("\nAfter black moves d7-d5:")
for row in gs.board:
    print(row)

print("enPassantPossible:", gs.enPassantPossible)

# Now get valid moves for white
all_moves = gs.getAllPossibleMoves()
print("\nAll possible moves for white:")
for move in all_moves:
    if move.pieceMoved == "wp":
        print(move.getChessNotation(), "en passant:", move.isEnPassantMove)

# Check if white is in check
print("Is white in check?", gs.inCheck())

valid_moves = gs.getValidMoves()

print("\nValid moves for white:")
for move in valid_moves:
    if move.pieceMoved == "wp":
        print(move.getChessNotation(), "en passant:", move.isEnPassantMove)

# Try to find the en passant move
en_passant_move = None
for move in valid_moves:
    if move.isEnPassantMove:
        en_passant_move = move
        break

if en_passant_move:
    print("En passant move found:", en_passant_move.getChessNotation())
    gs.makeMove(en_passant_move)
    print("\nAfter en passant:")
    for row in gs.board:
        print(row)
else:
    print("No en passant move found!")