import random
import time

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 6
endTime = 0

# Zobrist keys
# We need random numbers for:
# - 12 piece types (wP, wN, wB, wR, wQ, wK, bP, bN, bB, bR, bQ, bK) on 64 squares
# - Castling rights (4 bits: wks, wqs, bks, bqs)
# - En Passant file (8 files or None)
# - Turn (White or Black)

zobrist_table = [[[random.getrandbits(64) for _ in range(8)] for _ in range(8)] for _ in range(12)]
zobrist_castling = [random.getrandbits(64) for _ in range(4)]
zobrist_enpassant = [random.getrandbits(64) for _ in range(8)]
zobrist_turn = random.getrandbits(64)

# Map your piece strings to indices 0-11
piece_map = {
    "wp": 0, "wN": 1, "wB": 2, "wR": 3, "wQ": 4, "wK": 5,
    "bp": 6, "bN": 7, "bB": 8, "bR": 9, "bQ": 10, "bK": 11
}


def compute_hash(gs):
    h = 0
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != "--":
                idx = piece_map[piece]
                h ^= zobrist_table[idx][r][c]

    if gs.currentCastlingRights.wks: h ^= zobrist_castling[0]
    if gs.currentCastlingRights.wqs: h ^= zobrist_castling[1]
    if gs.currentCastlingRights.bks: h ^= zobrist_castling[2]
    if gs.currentCastlingRights.bqs: h ^= zobrist_castling[3]

    if hasattr(gs, 'enpassantPossible') and gs.enpassantPossible != ():
        h ^= zobrist_enpassant[gs.enpassantPossible[1]]

    if gs.whiteToMove:
        h ^= zobrist_turn

    return h

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
    # The actual table: Dictionary mapping Hash -> Entry
    transposition_table = {}

    # Constants for Flags
    HASH_EXACT = 0  # We found an exact score (PV node)
    HASH_ALPHA = 1  # We failed low (score <= alpha) (Upper bound)
    HASH_BETA = 2  # We failed high (score >= beta) (Lower bound)

    @staticmethod
    def findRandomMove(validMoves):
        if not validMoves:
            return None
        return random.choice(validMoves)


    @staticmethod
    def is_endgame(gs):
        """Don't use null move in endgames - zugzwang is common"""
        piece_count = 0
        for row in gs.board:
            for square in row:
                if square != "--" and square[1] != 'K':
                    piece_count += 1
        return piece_count <= 6  # Adjust threshold as needed

    @staticmethod
    def findBestMove(gs, validMoves):
        global nextMove, counter, endTime
        nextMove = None
        random.shuffle(validMoves)
        counter = 0
        THINK_TIME = 2.0
        endTime = time.time() + THINK_TIME

        current_depth = 1

        while True:
            if time.time() >= endTime:
                break

            print(f"--- Starting Search at Depth {current_depth} ---")
            try:
                # FIXED CALL: We pass 'current_depth' twice.
                # Once as the "countdown" (depth) and once as the "identifier" (rootDepth)
                score = SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                    gs, validMoves, current_depth, -CHECKMATE, CHECKMATE,
                    1 if gs.whiteToMove else -1, current_depth
                )

                if score == CHECKMATE or score == -CHECKMATE:
                    break
                current_depth += 1

                # Optimization: Put best move first for next loop
                if nextMove in validMoves:
                    validMoves.insert(0, validMoves.pop(validMoves.index(nextMove)))

            except TimeoutError:
                break

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
    def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, rootDepth):
        global nextMove, counter, endTime
        counter += 1

        # 1. TIME CHECK
        if counter % 1000 == 0:
            if time.time() >= endTime:
                raise TimeoutError("Time Limit")

        # 2. TT LOOKUP (Must be at the very top!)
        board_hash = compute_hash(gs)
        if board_hash in SmartMoveFinder.transposition_table:
            entry = SmartMoveFinder.transposition_table[board_hash]
            if entry['depth'] >= depth:
                score = entry['score']
                flag = entry['flag']

                if flag == SmartMoveFinder.HASH_EXACT:
                    return score
                elif flag == SmartMoveFinder.HASH_ALPHA and score <= alpha:
                    return alpha
                elif flag == SmartMoveFinder.HASH_BETA and score >= beta:
                    return beta

        # 3. BASE CASES
        if depth == 0:
            return SmartMoveFinder.quiescenceSearch(gs, alpha, beta, turnMultiplier)

        if len(validMoves) == 0:
            if gs.checkMate:
                return -CHECKMATE
            return STALEMATE

        # 4. MOVE ORDERING
        # Optimization: If TT suggests a move, try it first!
        tt_best_move = None
        if board_hash in SmartMoveFinder.transposition_table:
            tt_best_move = SmartMoveFinder.transposition_table[board_hash].get('best_move')

        def score_move(move):
            if move == tt_best_move:
                return 1000  # Try TT move first!
            if move.pieceCaptured != '--':
                captured_piece_type = move.pieceCaptured[1]
                return 10 * pieceScore.get(captured_piece_type, 0)
            if move.isPawnPromotion:
                return 9
            return 0

        validMoves.sort(key=score_move, reverse=True)

        # 5. MAIN SEARCH LOOP
        original_alpha = alpha
        best_move_local = None
        maxScore = -CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            try:
                score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha,
                                                                  -turnMultiplier, rootDepth)
            finally:
                gs.undoMove()

            if score > maxScore:
                maxScore = score
                best_move_local = move
                if depth == rootDepth:
                    nextMove = move
                if maxScore == CHECKMATE:
                    break

            if maxScore > alpha:
                alpha = maxScore

            if alpha >= beta:
                break

        # 6. TT STORE (Must be at the very end!)
        if maxScore <= original_alpha:
            flag = SmartMoveFinder.HASH_ALPHA
        elif maxScore >= beta:
            flag = SmartMoveFinder.HASH_BETA
        else:
            flag = SmartMoveFinder.HASH_EXACT

        # Only store if not a mate score (to avoid depth bugs)
        if abs(maxScore) < 500:
            SmartMoveFinder.transposition_table[board_hash] = {
                'score': maxScore,
                'depth': depth,
                'flag': flag,
                'best_move': best_move_local
            }

        if (depth >= 3 and
                not gs.inCheck() and
                not gs.is_endgame(gs) and
                turnMultiplier * SmartMoveFinder.scoreBoard(gs) > beta):  # Null move only when we're doing well

            # Make a "null move" - just flip the turn
            gs.whiteToMove = not gs.whiteToMove

            # Search with reduced depth (R = 2 or 3)
            R = 2  # Reduction factor
            score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                gs, gs.getValidMoves(), depth - 1 - R, -beta, -beta + 1,
                -turnMultiplier, rootDepth
            )

            # Undo the null move
            gs.whiteToMove = not gs.whiteToMove

            if score >= beta:
                # Verify with a shallow search to catch zugzwang
                if depth >= 6:  # Only for deep searches
                    verify_score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                        gs, validMoves, depth - R, -beta, -beta + 1,
                        -turnMultiplier, rootDepth
                    )
                    if verify_score >= beta:
                        return beta  # Confirmed cutoff
                else:
                    return beta  # Trust it for shallow depths
        return maxScore

    @classmethod
    def is_candidate_passed_pawn(cls, gs, row, col, color):
        """
        Check if a pawn is a candidate passed pawn

        A candidate is a pawn that:
        1. Is NOT currently passed
        2. Has equal or more friendly pawns than enemy pawns on its file + adjacent files

        Args:
            gs: Game state
            row, col: Position of the pawn
            color: 'w' or 'b'

        Returns:
            True if candidate passer, False otherwise
        """

        # If it's already passed, it's not a "candidate"
        if cls.is_passed_pawn(gs, row, col, color):
            return False

        friendly_pawn = 'wp' if color == 'w' else 'bp'
        enemy_pawn = 'bp' if color == 'w' else 'wp'

        # Count pawns on this file and adjacent files
        friendly_count = 0
        enemy_count = 0

        # Files to check: left (col-1), center (col), right (col+1)
        files_to_check = []
        if col > 0:
            files_to_check.append(col - 1)
        files_to_check.append(col)
        if col < 7:
            files_to_check.append(col + 1)

        # Determine which ranks to count based on color
        if color == 'w':
            # For white: only count pawns in front (rows 0 to row)
            start_row = 0
            end_row = row + 1  # Include current pawn
        else:
            # For black: only count pawns in front (rows row to 7)
            start_row = row
            end_row = 8

        # Count pawns
        for check_col in files_to_check:
            for check_row in range(start_row, end_row):
                square = gs.board[check_row][check_col]

                if square == friendly_pawn:
                    friendly_count += 1
                elif square == enemy_pawn:
                    enemy_count += 1

        # Candidate if we have at least as many pawns as opponent
        return friendly_count >= enemy_count

    @classmethod
    def candidate_passed_pawn_value(cls, gs, row, col, color):
        """
        Calculate bonus for candidate passed pawns

        Typically worth 30-50% of a passed pawn's value
        """

        # Base value by rank (smaller than passed pawns)
        if color == 'w':
            rank = 7 - row
            # Candidates on ranks 4-6 are most valuable
            rank_bonus = [0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.4, 0][rank]
        else:
            rank = row
            rank_bonus = [0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.4, 0][rank]

        bonus = rank_bonus

        # === MAJORITY BONUS ===
        # If we have significantly more pawns, the candidate is stronger
        friendly_pawn = 'wp' if color == 'w' else 'bp'
        enemy_pawn = 'bp' if color == 'w' else 'wp'

        files_to_check = []
        if col > 0:
            files_to_check.append(col - 1)
        files_to_check.append(col)
        if col < 7:
            files_to_check.append(col + 1)

        if color == 'w':
            start_row = 0
            end_row = row + 1
        else:
            start_row = row
            end_row = 8

        friendly_count = 0
        enemy_count = 0

        for check_col in files_to_check:
            for check_row in range(start_row, end_row):
                square = gs.board[check_row][check_col]
                if square == friendly_pawn:
                    friendly_count += 1
                elif square == enemy_pawn:
                    enemy_count += 1

        # Bonus based on pawn majority
        pawn_advantage = friendly_count - enemy_count
        if pawn_advantage >= 2:
            bonus *= 1.5  # Strong candidate (2+ pawn advantage)
        elif pawn_advantage == 1:
            bonus *= 1.2  # Good candidate (1 pawn advantage)
        # If equal (advantage = 0), no multiplier

        # === ADVANCED CANDIDATE ===
        # Candidates on ranks 5-6 (white) or 2-3 (black) are very dangerous
        if color == 'w' and row <= 2:  # Ranks 6-7
            bonus *= 1.3
        elif color == 'b' and row >= 5:  # Ranks 2-3
            bonus *= 1.3

        return bonus

    @classmethod
    def is_doubled_pawn(cls, gs, row, col, color):
        """
        Check if a pawn has another friendly pawn on the same file

        Returns:
            True if doubled, False otherwise
        """
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        # Search the entire file (same col) for other friendly pawns
        for check_row in range(8):
            if check_row == row:  # Skip the pawn itself
                continue

            if gs.board[check_row][col] == friendly_pawn:
                return True  # Found another pawn on same file

        return False

    @classmethod
    def is_isolated_pawn(cls, gs, row, col, color):
        """
        Check if a pawn has no friendly pawns on adjacent files

        Returns:
            True if isolated, False otherwise
        """
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        # Check left file (col - 1)
        if col > 0:
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    return False  # Found a neighbor on left

        # Check right file (col + 1)
        if col < 7:
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    return False  # Found a neighbor on right

        return True  # No neighbors found = isolated

    @classmethod
    def is_backward_pawn(cls, gs, row, col, color):
        """
        Check if a pawn is backward

        A pawn is backward if:
        1. It cannot safely advance (enemy pawn controls the square ahead)
        2. All friendly pawns on adjacent files are ahead of it

        Returns:
            True if backward, False otherwise
        """
        friendly_pawn = 'wp' if color == 'w' else 'bp'
        enemy_pawn = 'bp' if color == 'w' else 'wp'

        # === STEP 1: Check if pawn can safely advance ===
        if color == 'w':
            # White pawns move up (decreasing row)
            target_square = row - 1

            if target_square < 0:  # Can't move off board
                return False

            # Check if square ahead is blocked
            if gs.board[target_square][col] != '--':
                return False  # Blocked by a piece (not backward, just stuck)

            # Check if enemy pawns control the square ahead
            can_advance_safely = True

            # Check left diagonal (col - 1)
            if col > 0 and target_square > 0:
                if gs.board[target_square - 1][col - 1] == enemy_pawn:
                    can_advance_safely = False

            # Check right diagonal (col + 1)
            if col < 7 and target_square > 0:
                if gs.board[target_square - 1][col + 1] == enemy_pawn:
                    can_advance_safely = False

            if can_advance_safely:
                return False  # Can advance safely = not backward

        else:  # Black
            # Black pawns move down (increasing row)
            target_square = row + 1

            if target_square >= 8:
                return False

            if gs.board[target_square][col] != '--':
                return False

            can_advance_safely = True

            # Check left diagonal
            if col > 0 and target_square < 7:
                if gs.board[target_square + 1][col - 1] == enemy_pawn:
                    can_advance_safely = False

            # Check right diagonal
            if col < 7 and target_square < 7:
                if gs.board[target_square + 1][col + 1] == enemy_pawn:
                    can_advance_safely = False

            if can_advance_safely:
                return False

        # === STEP 2: Check if all neighbors are ahead ===
        has_neighbors = False
        all_neighbors_ahead = True

        # Check left file
        if col > 0:
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    has_neighbors = True

                    # Check if this neighbor is ahead
                    if color == 'w' and check_row >= row:
                        all_neighbors_ahead = False
                    elif color == 'b' and check_row <= row:
                        all_neighbors_ahead = False

        # Check right file
        if col < 7:
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    has_neighbors = True

                    if color == 'w' and check_row >= row:
                        all_neighbors_ahead = False
                    elif color == 'b' and check_row <= row:
                        all_neighbors_ahead = False

        # Backward if has neighbors AND they're all ahead
        return has_neighbors and all_neighbors_ahead

    @classmethod
    def evaluate_pawn_weaknesses(cls, gs):
        """
        Optimized: Avoid over-penalizing pawns with multiple weaknesses
        """
        penalty = 0

        for row in range(8):
            for col in range(8):
                square = gs.board[row][col]

                if square in ['wp', 'bp']:
                    color = 'w' if square == 'wp' else 'b'
                    pawn_penalty = 0

                    # Check all weaknesses
                    is_doubled = cls.is_doubled_pawn(gs, row, col, color)
                    is_isolated = cls.is_isolated_pawn(gs, row, col, color)
                    is_backward = cls.is_backward_pawn(gs, row, col, color)

                    # === CALCULATE PENALTY ===

                    # Doubled + Isolated = "Doubled Isolated" (worst case)
                    if is_doubled and is_isolated:
                        pawn_penalty = 0.6  # Severe penalty

                    # Just doubled
                    elif is_doubled:
                        pawn_penalty = 0.3

                    # Just isolated
                    elif is_isolated:
                        if cls.is_endgame(gs):
                            pawn_penalty = 0.35
                        else:
                            pawn_penalty = 0.25

                    # Just backward
                    elif is_backward:
                        pawn_penalty = 0.2

                    # Apply penalty
                    if color == 'w':
                        penalty -= pawn_penalty
                    else:
                        penalty += pawn_penalty

        return penalty

    @staticmethod
    def evaluate_passed_pawns(gs):
        """
        Evaluate passed pawns AND candidate passed pawns for both sides
        """
        score = 0

        for row in range(8):
            for col in range(8):
                square = gs.board[row][col]

                if square == 'wp':  # White pawn
                    # Check for passed pawn first
                    if SmartMoveFinder.is_passed_pawn(gs, row, col, 'w'):
                        bonus = SmartMoveFinder.passed_pawn_value(gs, row, col, 'w')
                        score += bonus

                    # If not passed, check for candidate
                    elif SmartMoveFinder.is_candidate_passed_pawn(gs, row, col, 'w'):
                        bonus = SmartMoveFinder.candidate_passed_pawn_value(gs, row, col, 'w')
                        score += bonus

                elif square == 'bp':  # Black pawn
                    if SmartMoveFinder.is_passed_pawn(gs, row, col, 'b'):
                        bonus = SmartMoveFinder.passed_pawn_value(gs, row, col, 'b')
                        score -= bonus

                    elif SmartMoveFinder.is_candidate_passed_pawn(gs, row, col, 'b'):
                        bonus = SmartMoveFinder.candidate_passed_pawn_value(gs, row, col, 'b')
                        score -= bonus

        return score

    @staticmethod
    def is_passed_pawn(gs, row, col, color):
        """
        Check if a pawn at (row, col) is passed

        For WHITE pawn: Check rows 0 to row-1 (ahead) on files col-1, col, col+1
        For BLACK pawn: Check rows row+1 to 7 (ahead) on files col-1, col, col+1
        """
        if color == 'w':
            # White pawns move "up" (decreasing row numbers)
            enemy = 'bp'
            start_row = 0
            end_row = row

        else:  # Black
            # Black pawns move "down" (increasing row numbers)
            enemy = 'wp'
            start_row = row + 1
            end_row = 8

        # Check the three files: left, center, right
        files_to_check = []
        if col > 0:
            files_to_check.append(col - 1)  # Left file
        files_to_check.append(col)  # Same file
        if col < 7:
            files_to_check.append(col + 1)  # Right file

        # Look for enemy pawns
        for check_row in range(start_row, end_row):
            for check_col in files_to_check:
                if gs.board[check_row][check_col] == enemy:
                    return False  # Found an enemy pawn blocking

        return True  # No blockers found = passed!

    @staticmethod
    def passed_pawn_value(gs, row, col, color):
        """
        Calculate the value of a passed pawn
        Considers: rank, support, king distance, etc.
        """

        # === 1. BASE VALUE BY RANK ===
        if color == 'w':
            rank = 7 - row  # White: rank 2 = row 6, rank 7 = row 1
            # Values: [impossible, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 3.5]
            rank_bonus = [0, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 3.5][rank]
        else:
            rank = row  # Black: rank 2 = row 1, rank 7 = row 6
            rank_bonus = [0, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 3.5][rank]

        bonus = rank_bonus

        # === 2. FRIENDLY PAWN SUPPORT ===
        # Check if friendly pawns protect this pawn
        supported = False
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        if color == 'w':
            support_row = row + 1  # Check rank behind
            if support_row < 8:
                if col > 0 and gs.board[support_row][col - 1] == friendly_pawn:
                    supported = True
                if col < 7 and gs.board[support_row][col + 1] == friendly_pawn:
                    supported = True
        else:
            support_row = row - 1
            if support_row >= 0:
                if col > 0 and gs.board[support_row][col - 1] == friendly_pawn:
                    supported = True
                if col < 7 and gs.board[support_row][col + 1] == friendly_pawn:
                    supported = True

        if supported:
            bonus *= 1.3  # 30% bonus for protected passed pawns

        # === 3. KING DISTANCE (Endgame Only) ===
        if SmartMoveFinder.is_endgame(gs):
            # Find kings
            white_king_pos = None
            black_king_pos = None

            for r in range(8):
                for c in range(8):
                    if gs.board[r][c] == 'wK':
                        white_king_pos = (r, c)
                    elif gs.board[r][c] == 'bK':
                        black_king_pos = (r, c)

            if white_king_pos and black_king_pos:
                # Distance to promotion square
                if color == 'w':
                    promo_square = (0, col)  # 8th rank
                    friendly_king = white_king_pos
                    enemy_king = black_king_pos
                else:
                    promo_square = (7, col)  # 1st rank
                    friendly_king = black_king_pos
                    enemy_king = white_king_pos

                # Chebyshev distance (max of row/col difference)
                friendly_dist = max(abs(friendly_king[0] - promo_square[0]),
                                    abs(friendly_king[1] - promo_square[1]))
                enemy_dist = max(abs(enemy_king[0] - promo_square[0]),
                                 abs(enemy_king[1] - promo_square[1]))

                # If our king is closer, bonus. If enemy king is closer, penalty
                king_diff = enemy_dist - friendly_dist
                bonus += king_diff * 0.15  # Each square of advantage is worth 0.15

        # === 4. BLOCKADED PENALTY ===
        # If an enemy piece is directly in front, it's blockaded
        if color == 'w':
            block_row = row - 1
            if block_row >= 0 and gs.board[block_row][col] != '--':
                if gs.board[block_row][col][0] == 'b':  # Enemy piece
                    bonus *= 0.6  # 40% penalty
        else:
            block_row = row + 1
            if block_row < 8 and gs.board[block_row][col] != '--':
                if gs.board[block_row][col][0] == 'w':
                    bonus *= 0.6

        # === 5. UNSTOPPABLE BONUS ===
        # In endgames, if the pawn can promote before the enemy king can catch it
        if SmartMoveFinder.is_endgame(gs) and rank >= 5:
            if color == 'w':
                moves_to_promote = rank  # Rank 6 = 1 move, rank 7 = 0 moves
                if black_king_pos:
                    enemy_king_dist = max(abs(black_king_pos[0] - 0),
                                          abs(black_king_pos[1] - col))

                    # Simple unstoppable check (not perfect, but good heuristic)
                    if enemy_king_dist > moves_to_promote + 1:
                        bonus += 5.0  # Huge bonus for unstoppable pawns
            else:
                moves_to_promote = 7 - rank
                if white_king_pos:
                    enemy_king_dist = max(abs(white_king_pos[0] - 7),
                                          abs(white_king_pos[1] - col))
                    if enemy_king_dist > moves_to_promote + 1:
                        bonus += 5.0
                        
        # === 6. CONNECTED PASSED PAWNS ===
        if SmartMoveFinder.has_connected_passer(gs, row, col, color):
            bonus *= 1.5  # 50% bonus

        # If passed pawn is far from kings
        if SmartMoveFinder.is_endgame(gs):
            if col <= 2 or col >= 5:
                bonus *= 1.2

        return bonus



    @classmethod
    def has_connected_passer(cls, gs, row, col, color):
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        # Check left file (col - 1)
        if col > 0:  # Bounds check
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    # Found a friendly pawn - check if it's also passed
                    if cls.is_passed_pawn(gs, check_row, col - 1, color):
                        # Check if close enough (within 2 ranks)
                        if abs(check_row - row) <= 2:
                            return True

        # Check right file (col + 1)
        if col < 7:  # Bounds check
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    # Found a friendly pawn - check if it's also passed
                    if cls.is_passed_pawn(gs, check_row, col + 1, color):
                        # Check if close enough (within 2 ranks)
                        if abs(check_row - row) <= 2:
                            return True

        return False

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

        # Passed pawns
        score += SmartMoveFinder.evaluate_passed_pawns(gs)

        # Pawn weaknesses
        score += SmartMoveFinder.evaluate_pawn_weaknesses(gs)

        return score