import ChessEngine

gs = ChessEngine.GameState()

# Move the bishop from f1 and knight from g1 to allow kingside castling
# f1 (7,5) to g2 (6,6)
move_bishop = ChessEngine.Move((7,5), (6,6), gs.board)
gs.makeMove(move_bishop)
# g1 (7,6) to h3 (5,7)
move_knight = ChessEngine.Move((7,6), (5,7), gs.board)
gs.makeMove(move_knight)

print("After moving bishop:")
for row in gs.board:
    print(row)

# Check castling rights
print("Castling rights:", gs.currentCastlingRights.wks, gs.currentCastlingRights.wqs)

# Get all possible moves
all_moves = gs.getAllPossibleMoves()
castle_moves = [move for move in all_moves if move.isCastleMove]
print("Castle moves:", len(castle_moves))
for move in castle_moves:
    print(move.getChessNotation(), "castle:", move.isCastleMove)

# Check valid moves
valid_moves = gs.getValidMoves()
valid_castle_moves = [move for move in valid_moves if move.isCastleMove]
print("Valid castle moves:", len(valid_castle_moves))
for move in valid_castle_moves:
    print(move.getChessNotation(), "castle:", move.isCastleMove)

# Try to make a kingside castle if available
if valid_castle_moves:
    move = valid_castle_moves[0]
    print("Making move:", move.getChessNotation())
    gs.makeMove(move)
    print("Board after castle:")
    for row in gs.board:
        print(row)
    print("King position:", gs.whiteKingPosition)
else:
    print("No castle moves available")