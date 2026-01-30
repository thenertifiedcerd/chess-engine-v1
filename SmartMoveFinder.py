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

rookScores = [[2, 1, 2, 3, 3, 3, 2, 2], # Centralizing on back rank is slightly better
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

    @staticmethod
    def quiescenceSearch(gs, alpha, beta, turnMultiplier):
        # Stand pat evaluation
        stand_pat = turnMultiplier * SmartMoveFinder.scoreBoard(gs)
        # Hard pruning for optimization
        if stand_pat >= beta:
            return beta

        # --- DELTA PRUNING (The Speed Boost) ---
        # If current score + capturing a Queen is STILL worse than alpha, then there is no point searching capturing a pawn or rook. We are too far behind.
        # Note: We disable this if we are in endgame (few pieces) or if finding checkmate is priority, but for a simple engine, this saves massive time.
        delta = 9  # Value of a Queen
        # If stand_pat is SO BAD that even a Queen capture can't raise it above alpha, give up.
        if stand_pat < alpha - delta:
            return alpha

        # 3. Update Alpha
        if stand_pat > alpha:
            alpha = stand_pat

        # 4. Generate Moves
        validMoves = gs.getValidMoves()

        # Move Ordering (extremely important for optimization)
        def score_move(move):
            if move.pieceCaptured != '--':
                captured_piece_type = move.pieceCaptured[1]
                return 10 * pieceScore.get(captured_piece_type, 0)
            return 0

        validMoves.sort(key=score_move, reverse=True)

        # 5. Search Loop (captures only)
        for move in validMoves:
            if move.pieceCaptured != '--' or move.isPawnPromotion:
                gs.makeMove(move)
                score = -SmartMoveFinder.quiescenceSearch(gs, -beta, -alpha, -turnMultiplier)
                gs.undoMove()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        return alpha

    @staticmethod
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

    @staticmethod
    def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
        global nextMove, counter
        counter += 1

        if depth == 0:
            # Instead of returning immediately, enter Quiescence Search
            return SmartMoveFinder.quiescenceSearch(gs, alpha, beta, turnMultiplier)

        # If the game is over (no moves left), we must return the correct score immediately.
        # Otherwise, the loop below won't run, and it will default to -CHECKMATE.
        if len(validMoves) == 0:
            if gs.checkMate:
                 return -CHECKMATE
            else:
                 return STALEMATE

        # --- MOVE ORDERING LOGIC START ---
        # Instead of random.shuffle, we sort moves to look at best ones first.
        # We guess that captures and promotions are usually better moves.
        def score_move(move):
            score = 0

            # 1. Prioritize Captures
            # Assuming your Move class has 'pieceCaptured' (usually a string or None)
            # If your engine uses 'isCapture', you can check that instead.
            if move.pieceCaptured != '--':
                # Look up the score of the captured piece.
                # Note: You might need to adjust 'move.pieceCaptured[1]' depending on how you store piece strings (e.g. "wP")
                captured_piece_type = move.pieceCaptured[1]
                score += 10 * pieceScore.get(captured_piece_type, 0)

            # 2. Prioritize Promotions
            if move.isPawnPromotion:
                score += 9  # Value of a Queen

            return score

        # Sort the moves! High scores (captures) go first.
        validMoves.sort(key=score_move, reverse=True)
        # --- MOVE ORDERING LOGIC END ---

        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
            gs.undoMove()

            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
                    print(move, score)

                # Optimization: Stop searching if we found checkmate
                if maxScore == CHECKMATE:
                    break

            if maxScore > alpha:
                alpha = maxScore

            if alpha >= beta:
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

        # 1. EVALUATE PIECES (Material + Position)
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    # Determine piece type and color
                    piece_type = square[1]
                    piece_color = square[0]

                    # --- POSITION SCORE LOOKUP ---
                    # Logic:
                    # 1. Pawns have their own specific tables (wp/bp), so we access them directly.
                    # 2. Other pieces share a table. White needs to flip the table (7-row)
                    #    because the tables are defined from Black's perspective (Rank 8 at index 0).

                    if piece_type == 'p':
                        position_score = piecePositionScores[square][row][col]
                    else:
                        if piece_color == 'w':
                            position_score = piecePositionScores[piece_type][7 - row][col]
                        else:
                            position_score = piecePositionScores[piece_type][row][col]

                    # --- MATERIAL SCORE LOOKUP ---
                    material_score = pieceScore[piece_type]

                    # --- FINAL CALCULATION ---
                    if piece_color == 'w':
                        score += material_score + (position_score * 0.1)
                    elif piece_color == 'b':
                        score -= (material_score + (position_score * 0.1))

        # 2. EVALUATE CASTLING (Run once per board, not inside the loop!)

        # --- WHITE CASTLING BONUSES ---
        # Check Short Castle (White): King on g1 (7,6), Rook on f1 (7,5)
        if gs.board[7][6] == 'wK' and gs.board[7][5] == 'wR':
            score += 0.5

            # Check Long Castle (White): King on c1 (7,2), Rook on d1 (7,3)
        if gs.board[7][2] == 'wK' and gs.board[7][3] == 'wR':
            score += 0.5

        # Punishment for White losing castling rights without castling
        if gs.board[7][4] == 'wK':  # King still on e1
            # Assuming 'wks' (white king side) and 'wqs' are booleans in your castle rights object
            if not gs.currentCastlingRights.wks and not gs.currentCastlingRights.wqs:
                score -= 0.2

                # --- BLACK CASTLING BONUSES ---
        # Check Short Castle (Black): King on g8 (0,6), Rook on f8 (0,5)
        if gs.board[0][6] == 'bK' and gs.board[0][5] == 'bR':
            score -= 0.5  # Subtract because black advantage is negative

        # Check Long Castle (Black): King on c8 (0,2), Rook on d8 (0,3)
        if gs.board[0][2] == 'bK' and gs.board[0][3] == 'bR':
            score -= 0.5

        # Punishment for Black losing castling rights
        if gs.board[0][4] == 'bK':
            if not gs.currentCastlingRights.bks and not gs.currentCastlingRights.bqs:
                score += 0.2  # Add score (good for white)

        return score