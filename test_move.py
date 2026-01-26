import ChessEngine

gs = ChessEngine.GameState()
print('Initial whiteToMove:', gs.whiteToMove)
print('Board[6][4]:', gs.board[6][4])
move = ChessEngine.Move((6,4),(4,4), gs.board)
print('Move notation:', move.getChessNotation())
allmoves = gs.getAllPossibleMoves()
print('Total possible moves initially:', len(allmoves))
found = any(move == mv for mv in allmoves)
print('Move in all possible moves?:', found)
if found:
    for mv in allmoves:
        if move == mv:
            gs.makeMove(mv)
            break
print('After makeMove, board[6][4]:', gs.board[6][4], 'board[4][4]:', gs.board[4][4])
print('whiteToMove now:', gs.whiteToMove)
