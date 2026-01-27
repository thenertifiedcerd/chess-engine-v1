from SmartMoveFinder import SmartMoveFinder

### This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining valid moves at the current state. It will also be a move log.

class GameState:
    def __init__(self):
        # Board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'.
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'p'.
        # 'N' represents Knight.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () # coordinates for the square where en-passant capture is possible
        self.currentCastlingRights = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currentCastlingRights.wks,
                                             self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs,
                                             self.currentCastlingRights.bqs)]


    ### makeMove() will execute a move. This will not work for castling, pawn promotion, and en-passant.
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # --- FIX: Ensure these match "Position", not "Location" ---
        if move.pieceMoved == 'wK':
            self.whiteKingPosition = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingPosition = (move.endRow, move.endCol)
        # ----------------------------------------------------------

        # pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N: ")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # en passant capture
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # update enPassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # two square pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # move rook
                self.board[move.endRow][move.endCol + 1] = "--" # empty rook's original square
            else: # queenside
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # move rook
                self.board[move.endRow][move.endCol - 2] = "--" # empty rook's original square

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(self.currentCastlingRights.wks,
                                                 self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs,
                                                 self.currentCastlingRights.bqs))

    ### Undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0: # to confirm there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns back 
            if move.pieceMoved == "wK":
                self.whiteKingPosition = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingPosition = (move.startRow, move.startCol)

            # undoing en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            # undoing 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # undoing castling rights
            self.castleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
            lastRights = self.castleRightsLog[-1]
            self.currentCastlingRights.wks = lastRights.wks
            self.currentCastlingRights.bks = lastRights.bks
            self.currentCastlingRights.wqs = lastRights.wqs
            self.currentCastlingRights.bqs = lastRights.bqs

            # undo castling move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] # move rook back
                    self.board[move.endRow][move.endCol - 1] = "--" # empty square
                else: # queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1] # move rook back
                    self.board[move.endRow][move.endCol + 1] = "--" # empty square



    ### All moves considering checks

    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = castleRights(self.currentCastlingRights.wks,
                                        self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs,
                                        self.currentCastlingRights.bqs)
        # generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingPosition[0], self.whiteKingPosition[1], moves)
        else:
            self.getCastleMoves(self.blackKingPosition[0], self.blackKingPosition[1], moves)
        # make the moves
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # generate all opponent's moves
            # oppMoves = self.getAllPossibleMoves()
        # see if these moves attack the king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # if they attack the king, then it's invalid
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
                print("Checkmate!")
            else:
                self.staleMate = True
                print("Stalemate!")
        else:
            self.checkMate = False
            self.staleMate = False

        self.enPassantPossible = tempEnPassantPossible
        return moves
    
    # determine if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingPosition[0], self.whiteKingPosition[1])
        else:
            return self.squareUnderAttack(self.blackKingPosition[0], self.blackKingPosition[1])


    # determine if the enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # switch to opponent's view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    # All moves without checks

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                # --- CRITICAL CHECK: Do you have the Black turn logic here? ---
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # --------------------------------------------------------------

                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves
    
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # white pawn moves (move up the board, decreasing row)
            # forward one
            if r-1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                # forward two from starting rank
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            # captures
            if c-1 >= 0 and r-1 >= 0:
                target = self.board[r-1][c-1]
                if target != "--" and target[0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c-1), self.board, isEnPassantMove = True))

            if c+1 <= 7 and r-1 >= 0:
                target = self.board[r-1][c+1]
                if target != "--" and target[0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r - 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c+1), self.board, isEnPassantMove = True))

        else: # black pawn moves (move down the board, increasing row)
            # forward one
            if r+1 <= 7 and self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                # forward two from starting rank
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            # captures
            if c-1 >= 0 and r+1 <= 7:
                target = self.board[r+1][c-1]
                if target != "--" and target[0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r + 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove = True))
            if c+1 <= 7 and r+1 <= 7:
                target = self.board[r+1][c+1]
                if target != "--" and target[0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r + 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove = True))

            # add pawm promotion later on
                    
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1,0), (0, 1)) # up, down, left, write
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # make sure the square is on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break # friendly piece invalid
                else:
                    break # off board



    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))
   
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # four diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # make sure the square is on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break # friendly piece invalid
                else:
                    break # off board
   
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
   
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.bks = False
        
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))


class castleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0} 
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        if isEnPassantMove:
            self.pieceCaptured = board[self.startRow][self.endCol]
        else:
            self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        # En passant
        self.isEnPassantMove = False
        self.isEnPassantMove = isEnPassantMove
        # Castle move
        self.isCastleMove = isCastleMove
        # unique move ID
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.pieceMoved[1] + self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
