import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

rookScores = [[2, 1, 1, 2, 2, 1, 1, 2], # Centralizing on back rank is slightly better
             [1, 2, 2, 2, 2, 2, 2, 1],
             [1, 2, 2, 2, 2, 2, 2, 1],
             [1, 2, 2, 2, 2, 2, 2, 1],
             [1, 2, 2, 2, 2, 2, 2, 1],
             [1, 2, 2, 2, 2, 2, 2, 1],
             [2, 2,  2, 2, 2, 2, 2, 2], # The 7th rank is powerful for Rooks
             [2, 1, 1, 2, 2, 1, 1, 2]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0], # Impossible rank
                 [1, 1, 1, 0, 0, 1, 1, 1], # Starting rank (encourage d/e push by scoring current square lower)
                 [1, 1, 2, 3, 3, 2, 1, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 5, 5, 4, 3, 2],
                 [3, 4, 5, 6, 6, 5, 4, 3],
                 [5, 6, 7, 8, 8, 7, 6, 5], # Close to promotion
                 [9, 9, 9, 9, 9, 9, 9, 9]]  # Promotion rank (pawn becomes a Queen)

whitePawnScores = [[9, 9, 9, 9, 9, 9, 9, 9],     # rank 8 (black's starting rank)
                 [5, 6, 7, 8, 8, 7, 6, 5],     # rank 7 — close to promotion for black
                 [3, 4, 5, 6, 6, 5, 4, 3],
                 [2, 3, 4, 5, 5, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 1, 2, 3, 3, 2, 1, 1],
                 [1, 1, 1, 0, 0, 1, 1, 1],     # rank 2 — black wants to push d/e-pawns here
                 [0, 0, 0, 0, 0, 0, 0, 0]]     # rank 1 — black's impossible rank (first rank)

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 1, 2, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]]

kingScores = [[3, 4, 2, 1, 1, 2, 4, 3], # Corners (g1/b1) are safest
             [2, 3, 1, 0, 0, 1, 3, 2], # Pawn shield area
             [1, 1, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0], # Center is dangerous
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]

piecePositionScores = {"N": knightScores, "Q": queenScores, "K": kingScores, "B": bishopScores, "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}

class SmartMoveFinder:

    @staticmethod
    def findRandomMove(validMoves):
        return validMoves[random.randint(0, len(validMoves) - 1)]

    # 1. HELPER METHOD: Sets up the first call
    @staticmethod
    def findBestMove(gs, validMoves):
        global nextMove, counter
        nextMove = None
        random.shuffle(validMoves)
        counter = 0
        # We pass gs.whiteToMove as a VALUE, not a parameter definition
        # SmartMoveFinder.findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
        # SmartMoveFinder.findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
        SmartMoveFinder.findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
        print(f"After your move, the AI evaluated {counter} moves")
        return nextMove

    # 2. RECURSIVE METHOD: The actual algorithm
    @staticmethod
    def findMoveMinMax(gs, validMoves, depth, whiteToMove):
        global nextMove
        # Base case: we are at the bottom of the tree
        if depth == 0:
            return SmartMoveFinder.scoreBoard(gs)
        if whiteToMove: # White's turn (Maximizing)
            maxScore = -CHECKMATE
            for move in validMoves:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                # Recursive call
                score = SmartMoveFinder.findMoveMinMax(gs, nextMoves, depth - 1, False)
                if score > maxScore:
                    maxScore = score
                    if depth == DEPTH:
                        nextMove = move

                gs.undoMove()
            return maxScore

        else:  # Black's turn (Minimizing)
            minScore = CHECKMATE
            for move in validMoves:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                # Recursive call
                score = SmartMoveFinder.findMoveMinMax(gs, nextMoves, depth - 1, True)
                if score < minScore:
                    minScore = score
                    if depth == DEPTH:
                        nextMove = move

                gs.undoMove()
            return minScore

    def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
        global nextMove, counter
        counter += 1
        if depth == 0:
            return turnMultiplier * SmartMoveFinder.scoreBoard(gs)

        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -SmartMoveFinder.findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
        global nextMove, counter
        counter += 1
        if depth == 0:
            return turnMultiplier * SmartMoveFinder.scoreBoard(gs)
        random.shuffle(validMoves) # alpha-beta pruning works better with random shuffling, best with move ordering

        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier,)
            gs.undoMove()
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
                    print(move, score)

            if maxScore > alpha:
                alpha = maxScore

            if alpha >= beta: # The cutoff
                break


        return maxScore

    # 3. SCORING METHOD
    @staticmethod
    def scoreBoard(gs):
        if gs.checkMate:
            if gs.whiteToMove:
                return -CHECKMATE  # Black wins
            else:
                return CHECKMATE  # White wins
        elif gs.staleMate:
            return STALEMATE

        score = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    # score positionally
                    piecePositionScore = 0
                    if square[1] != "K":
                        if square[1] == "p":
                            if square[1] == "p":
                                piecePositionScore = piecePositionScores[square][row][col]
                            else:
                                piecePositionScore = piecePositionScores[square[1]][row][col]
                    #     piecePositionScore = piecePositionScores["N"][row][col]
                    # elif square[1] == "Q":
                    #     piecePositionScore = piecePositionScores["Q"][row][col]
                    # elif square[1] == "K":
                    #     piecePositionScore = piecePositionScores["K"][row][col]
                    # elif square[1] == "R":
                    #     piecePositionScore = piecePositionScores["R"][row][col]
                    # elif square[1] == "B":
                    #     piecePositionScore = piecePositionScores["B"][row][col]
                    # elif square[1] == "p":
                    #     piecePositionScore = piecePositionScores["p"][row][col]
                    # else:
                    #     pass

                    if square[0] == 'w':
                        score += pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] - piecePositionScore * .1
        return score