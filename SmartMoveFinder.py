import random
import time

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 6
endTime = 0

# Zobrist keys
zobrist_table = [[[random.getrandbits(64) for _ in range(8)] for _ in range(8)] for _ in range(12)]
zobrist_castling = [random.getrandbits(64) for _ in range(4)]
zobrist_enpassant = [random.getrandbits(64) for _ in range(8)]
zobrist_turn = random.getrandbits(64)

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

    if hasattr(gs, 'enPassantPossible') and gs.enPassantPossible != ():
        h ^= zobrist_enpassant[gs.enPassantPossible[1]]

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

rookScores = [[2, 1, 2, 3, 3, 3, 2, 2],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [2, 2, 2, 2, 2, 2, 2, 2],
              [2, 1, 1, 2, 2, 1, 1, 2]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 4, 5, 5, 4, 3, 2],
                   [3, 4, 5, 6, 6, 5, 4, 3],
                   [5, 6, 7, 8, 8, 7, 6, 5],
                   [9, 9, 9, 9, 9, 9, 9, 9]]

whitePawnScores = [row[:] for row in blackPawnScores[::-1]]

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

kingScores = [[3, 4, 2, 1, 1, 2, 4, 3],
              [2, 3, 1, 0, 0, 1, 3, 2],
              [1, 1, 0, 0, 0, 0, 1, 1],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0]]

kingScores_eg = [
    [-0.5, -0.3, -0.3, -0.2, -0.2, -0.3, -0.3, -0.5],
    [-0.3, -0.1, 0.0, 0.2, 0.2, 0.0, -0.1, -0.3],
    [-0.2, 0.1, 0.4, 0.6, 0.6, 0.4, 0.1, -0.2],
    [-0.1, 0.3, 0.6, 0.9, 0.9, 0.6, 0.3, -0.1],
    [-0.1, 0.3, 0.6, 0.9, 0.9, 0.6, 0.3, -0.1],
    [-0.2, 0.1, 0.4, 0.6, 0.6, 0.4, 0.1, -0.2],
    [-0.3, -0.1, 0.0, 0.2, 0.2, 0.0, -0.1, -0.3],
    [-0.5, -0.3, -0.3, -0.2, -0.2, -0.3, -0.3, -0.5]
]

piecePositionScores = {"N": knightScores, "Q": queenScores, "K": kingScores, "B": bishopScores, "R": rookScores,
                       "wp": whitePawnScores, "bp": blackPawnScores}


class SmartMoveFinder:
    # Transposition Table
    transposition_table = {}
    HASH_EXACT = 0
    HASH_ALPHA = 1
    HASH_BETA = 2

    # NEW: Killer Moves - stores 2 killer moves per depth
    killer_moves = [[None, None] for _ in range(100)]

    # NEW: History Heuristic - stores how good moves have been historically
    history_table = {}

    @staticmethod
    def clear_search_data():
        """Clear killer moves and history between searches"""
        SmartMoveFinder.killer_moves = [[None, None] for _ in range(100)]
        SmartMoveFinder.history_table = {}

    @staticmethod
    def store_killer(move, depth):
        """Store a killer move at this depth"""
        if SmartMoveFinder.killer_moves[depth][0] != move:
            SmartMoveFinder.killer_moves[depth][1] = SmartMoveFinder.killer_moves[depth][0]
            SmartMoveFinder.killer_moves[depth][0] = move

    @staticmethod
    def update_history(move, depth):
        """Update history heuristic - good moves get higher scores"""
        move_key = (move.startRow, move.startCol, move.endRow, move.endCol)
        if move_key not in SmartMoveFinder.history_table:
            SmartMoveFinder.history_table[move_key] = 0
        SmartMoveFinder.history_table[move_key] += depth * depth  # Depth squared bonus

    @staticmethod
    def get_history_score(move):
        """Get history score for move ordering"""
        move_key = (move.startRow, move.startCol, move.endRow, move.endCol)
        return SmartMoveFinder.history_table.get(move_key, 0)

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
        return piece_count <= 6

    @staticmethod
    def findBestMove(gs, validMoves):
        global nextMove, counter, endTime
        nextMove = None
        random.shuffle(validMoves)
        counter = 0
        THINK_TIME = 5.0  # Increased from 2.0 for stronger play
        endTime = time.time() + THINK_TIME

        # Clear search data at start of new search
        SmartMoveFinder.clear_search_data()

        current_depth = 1
        best_score = -CHECKMATE

        while True:
            if time.time() >= endTime:
                break

            print(f"--- Depth {current_depth} ---")
            try:
                score = SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                    gs, validMoves, current_depth, -CHECKMATE, CHECKMATE,
                    1 if gs.whiteToMove else -1, current_depth
                )

                best_score = score

                # If we found mate, no need to search deeper
                if abs(score) >= CHECKMATE - 100:
                    print(f"Mate found at depth {current_depth}")
                    break

                current_depth += 1

                # Move ordering: put best move first for next iteration
                if nextMove and nextMove in validMoves:
                    validMoves.remove(nextMove)
                    validMoves.insert(0, nextMove)

            except TimeoutError:
                print(f"Time's up! Stopped at depth {current_depth}")
                break

        print(f"Final depth: {current_depth}, Score: {best_score}, Positions: {counter}")
        return nextMove

    @staticmethod
    def quiescenceSearch(gs, alpha, beta, turnMultiplier):
        """Quiescence search with delta pruning"""
        stand_pat = turnMultiplier * SmartMoveFinder.scoreBoard(gs)

        if stand_pat >= beta:
            return beta

        # Delta pruning
        BIG_DELTA = 9  # Queen value
        if stand_pat < alpha - BIG_DELTA:
            return alpha

        if stand_pat > alpha:
            alpha = stand_pat

        validMoves = gs.getValidMoves()

        # Only search captures and promotions
        capture_moves = [m for m in validMoves if m.pieceCaptured != '--' or m.isPawnPromotion]

        # MVV-LVA ordering
        def mvv_lva_score(move):
            if move.isPawnPromotion:
                return 100
            if move.pieceCaptured != '--':
                victim = pieceScore.get(move.pieceCaptured[1], 0)
                attacker = pieceScore.get(move.pieceMoved[1], 0)
                return 10 * victim - attacker
            return 0

        capture_moves.sort(key=mvv_lva_score, reverse=True)

        for move in capture_moves:
            gs.makeMove(move)
            score = -SmartMoveFinder.quiescenceSearch(gs, -beta, -alpha, -turnMultiplier)
            gs.undoMove()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    @staticmethod
    def order_moves(validMoves, tt_best_move, depth):
        """
        Enhanced move ordering:
        1. TT/PV move (10000)
        2. Captures (MVV-LVA: 100-9000)
        3. Killer moves (8000-9000)
        4. History heuristic (0-7999)
        5. Other moves
        """
        scored_moves = []

        for move in validMoves:
            score = 0

            # 1. TT move gets highest priority
            if move == tt_best_move:
                score = 10000

            # 2. Captures (MVV-LVA)
            elif move.pieceCaptured != '--':
                victim_value = pieceScore.get(move.pieceCaptured[1], 0)
                attacker_value = pieceScore.get(move.pieceMoved[1], 0)
                score = 100 + (10 * victim_value - attacker_value)

            # 3. Promotions
            elif move.isPawnPromotion:
                score = 90

            # 4. Killer moves
            elif move == SmartMoveFinder.killer_moves[depth][0]:
                score = 80
            elif move == SmartMoveFinder.killer_moves[depth][1]:
                score = 70

            # 5. History heuristic
            else:
                history_score = SmartMoveFinder.get_history_score(move)
                score = min(history_score / 100, 60)  # Cap at 60

            scored_moves.append((score, move))

        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    @staticmethod
    def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, rootDepth):
        global nextMove, counter, endTime
        counter += 1

        # Time check
        if counter % 2000 == 0:
            if time.time() >= endTime:
                raise TimeoutError("Time Limit")

        # TT Probe
        board_hash = compute_hash(gs)
        tt_best_move = None

        if board_hash in SmartMoveFinder.transposition_table:
            entry = SmartMoveFinder.transposition_table[board_hash]
            tt_best_move = entry.get('best_move')

            if entry['depth'] >= depth:
                score = entry['score']
                flag = entry['flag']

                if flag == SmartMoveFinder.HASH_EXACT:
                    return score
                elif flag == SmartMoveFinder.HASH_ALPHA and score <= alpha:
                    return alpha
                elif flag == SmartMoveFinder.HASH_BETA and score >= beta:
                    return beta

        # Quiescence search at leaf nodes
        if depth == 0:
            return SmartMoveFinder.quiescenceSearch(gs, alpha, beta, turnMultiplier)

        # Checkmate/Stalemate detection
        if len(validMoves) == 0:
            if gs.checkMate:
                return -CHECKMATE
            return STALEMATE

        # NULL MOVE PRUNING (improved)
        # Only in non-endgame, non-check positions, at sufficient depth
        if (depth >= 3 and
                not gs.inCheck() and
                not SmartMoveFinder.is_endgame(gs) and
                turnMultiplier * SmartMoveFinder.scoreBoard(gs) >= beta):

            # Make null move
            gs.whiteToMove = not gs.whiteToMove

            # Adaptive reduction: deeper searches get bigger reductions
            R = 3 if depth >= 6 else 2

            score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                gs, gs.getValidMoves(), depth - 1 - R, -beta, -beta + 1,
                -turnMultiplier, rootDepth
            )

            gs.whiteToMove = not gs.whiteToMove

            if score >= beta:
                # Verification search for deep nodes
                if depth >= 8:
                    verify_score = SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                        gs, validMoves, depth - R, alpha, beta,
                        turnMultiplier, rootDepth
                    )
                    if verify_score >= beta:
                        return beta
                else:
                    return beta

        # MOVE ORDERING
        ordered_moves = SmartMoveFinder.order_moves(validMoves, tt_best_move, depth)

        # Main search loop
        original_alpha = alpha
        best_move_local = None
        maxScore = -CHECKMATE
        moves_searched = 0

        for move in ordered_moves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()

            try:
                # LATE MOVE REDUCTIONS (LMR)
                # Reduce search depth for later moves that are likely bad
                if (moves_searched >= 4 and
                        depth >= 3 and
                        move.pieceCaptured == '--' and
                        not move.isPawnPromotion and
                        not gs.inCheck()):

                    # Reduced depth search first
                    reduction = 1 if depth >= 6 else 0
                    if moves_searched >= 8:
                        reduction += 1

                    score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                        gs, nextMoves, depth - 1 - reduction, -alpha - 1, -alpha,
                        -turnMultiplier, rootDepth
                    )

                    # If it looks good, re-search at full depth
                    if score > alpha:
                        score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                            gs, nextMoves, depth - 1, -beta, -alpha,
                            -turnMultiplier, rootDepth
                        )
                else:
                    # Normal full-depth search
                    score = -SmartMoveFinder.findMoveNegaMaxAlphaBeta(
                        gs, nextMoves, depth - 1, -beta, -alpha,
                        -turnMultiplier, rootDepth
                    )
            finally:
                gs.undoMove()

            moves_searched += 1

            if score > maxScore:
                maxScore = score
                best_move_local = move
                if depth == rootDepth:
                    nextMove = move

            if maxScore > alpha:
                alpha = maxScore

            # Beta cutoff
            if alpha >= beta:
                # Store killer move for quiet moves
                if move.pieceCaptured == '--' and not move.isPawnPromotion:
                    SmartMoveFinder.store_killer(move, depth)
                    SmartMoveFinder.update_history(move, depth)
                break

        # TT Store
        if maxScore <= original_alpha:
            flag = SmartMoveFinder.HASH_ALPHA
        elif maxScore >= beta:
            flag = SmartMoveFinder.HASH_BETA
        else:
            flag = SmartMoveFinder.HASH_EXACT

        if abs(maxScore) < CHECKMATE - 100:
            SmartMoveFinder.transposition_table[board_hash] = {
                'score': maxScore,
                'depth': depth,
                'flag': flag,
                'best_move': best_move_local
            }

        return maxScore

    # [All the evaluation functions remain the same - is_passed_pawn, passed_pawn_value, etc.]
    # I'm keeping them for brevity but they should all be included

    @staticmethod
    def is_passed_pawn(gs, row, col, color):
        if color == 'w':
            enemy = 'bp'
            start_row = 0
            end_row = row
        else:
            enemy = 'wp'
            start_row = row + 1
            end_row = 8

        files_to_check = []
        if col > 0:
            files_to_check.append(col - 1)
        files_to_check.append(col)
        if col < 7:
            files_to_check.append(col + 1)

        for check_row in range(start_row, end_row):
            for check_col in files_to_check:
                if gs.board[check_row][check_col] == enemy:
                    return False

        return True

    @staticmethod
    def passed_pawn_value(gs, row, col, color):
        if color == 'w':
            rank = 7 - row
            rank_bonus = [0, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 3.5][rank]
        else:
            rank = row
            rank_bonus = [0, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 3.5][rank]

        bonus = rank_bonus

        supported = False
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        if color == 'w':
            support_row = row + 1
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
            bonus *= 1.3

        if SmartMoveFinder.is_endgame(gs):
            white_king_pos = None
            black_king_pos = None

            for r in range(8):
                for c in range(8):
                    if gs.board[r][c] == 'wK':
                        white_king_pos = (r, c)
                    elif gs.board[r][c] == 'bK':
                        black_king_pos = (r, c)

            if white_king_pos and black_king_pos:
                if color == 'w':
                    promo_square = (0, col)
                    friendly_king = white_king_pos
                    enemy_king = black_king_pos
                else:
                    promo_square = (7, col)
                    friendly_king = black_king_pos
                    enemy_king = white_king_pos

                friendly_dist = max(abs(friendly_king[0] - promo_square[0]),
                                    abs(friendly_king[1] - promo_square[1]))
                enemy_dist = max(abs(enemy_king[0] - promo_square[0]),
                                 abs(enemy_king[1] - promo_square[1]))

                king_diff = enemy_dist - friendly_dist
                bonus += king_diff * 0.15

        if color == 'w':
            block_row = row - 1
            if block_row >= 0 and gs.board[block_row][col] != '--':
                if gs.board[block_row][col][0] == 'b':
                    bonus *= 0.6
        else:
            block_row = row + 1
            if block_row < 8 and gs.board[block_row][col] != '--':
                if gs.board[block_row][col][0] == 'w':
                    bonus *= 0.6

        if SmartMoveFinder.has_connected_passer(gs, row, col, color):
            bonus *= 1.5

        if SmartMoveFinder.is_endgame(gs):
            if col <= 2 or col >= 5:
                bonus *= 1.2

        return bonus

    @classmethod
    def has_connected_passer(cls, gs, row, col, color):
        friendly_pawn = 'wp' if color == 'w' else 'bp'

        if col > 0:
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    if cls.is_passed_pawn(gs, check_row, col - 1, color):
                        if abs(check_row - row) <= 2:
                            return True

        if col < 7:
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    if cls.is_passed_pawn(gs, check_row, col + 1, color):
                        if abs(check_row - row) <= 2:
                            return True

        return False

    @classmethod
    def is_doubled_pawn(cls, gs, row, col, color):
        friendly_pawn = 'wp' if color == 'w' else 'bp'
        for check_row in range(8):
            if check_row == row:
                continue
            if gs.board[check_row][col] == friendly_pawn:
                return True
        return False

    @classmethod
    def is_isolated_pawn(cls, gs, row, col, color):
        friendly_pawn = 'wp' if color == 'w' else 'bp'
        if col > 0:
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    return False
        if col < 7:
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    return False
        return True

    @classmethod
    def is_backward_pawn(cls, gs, row, col, color):
        friendly_pawn = 'wp' if color == 'w' else 'bp'
        enemy_pawn = 'bp' if color == 'w' else 'wp'

        if color == 'w':
            target_square = row - 1
            if target_square < 0:
                return False
            if gs.board[target_square][col] != '--':
                return False

            can_advance_safely = True
            if col > 0 and target_square > 0:
                if gs.board[target_square - 1][col - 1] == enemy_pawn:
                    can_advance_safely = False
            if col < 7 and target_square > 0:
                if gs.board[target_square - 1][col + 1] == enemy_pawn:
                    can_advance_safely = False

            if can_advance_safely:
                return False
        else:
            target_square = row + 1
            if target_square >= 8:
                return False
            if gs.board[target_square][col] != '--':
                return False

            can_advance_safely = True
            if col > 0 and target_square < 7:
                if gs.board[target_square + 1][col - 1] == enemy_pawn:
                    can_advance_safely = False
            if col < 7 and target_square < 7:
                if gs.board[target_square + 1][col + 1] == enemy_pawn:
                    can_advance_safely = False

            if can_advance_safely:
                return False

        has_neighbors = False
        all_neighbors_ahead = True

        if col > 0:
            for check_row in range(8):
                if gs.board[check_row][col - 1] == friendly_pawn:
                    has_neighbors = True
                    if color == 'w' and check_row >= row:
                        all_neighbors_ahead = False
                    elif color == 'b' and check_row <= row:
                        all_neighbors_ahead = False

        if col < 7:
            for check_row in range(8):
                if gs.board[check_row][col + 1] == friendly_pawn:
                    has_neighbors = True
                    if color == 'w' and check_row >= row:
                        all_neighbors_ahead = False
                    elif color == 'b' and check_row <= row:
                        all_neighbors_ahead = False

        return has_neighbors and all_neighbors_ahead

    @classmethod
    def evaluate_pawn_weaknesses(cls, gs):
        penalty = 0
        for row in range(8):
            for col in range(8):
                square = gs.board[row][col]
                if square in ['wp', 'bp']:
                    color = 'w' if square == 'wp' else 'b'
                    pawn_penalty = 0

                    is_doubled = cls.is_doubled_pawn(gs, row, col, color)
                    is_isolated = cls.is_isolated_pawn(gs, row, col, color)
                    is_backward = cls.is_backward_pawn(gs, row, col, color)

                    if is_doubled and is_isolated:
                        pawn_penalty = 0.6
                    elif is_doubled:
                        pawn_penalty = 0.3
                    elif is_isolated:
                        pawn_penalty = 0.35 if cls.is_endgame(gs) else 0.25
                    elif is_backward:
                        pawn_penalty = 0.2

                    if color == 'w':
                        penalty -= pawn_penalty
                    else:
                        penalty += pawn_penalty
        return penalty

    @classmethod
    def is_candidate_passed_pawn(cls, gs, row, col, color):
        if cls.is_passed_pawn(gs, row, col, color):
            return False

        friendly_pawn = 'wp' if color == 'w' else 'bp'
        enemy_pawn = 'bp' if color == 'w' else 'wp'

        friendly_count = 0
        enemy_count = 0

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

        for check_col in files_to_check:
            for check_row in range(start_row, end_row):
                square = gs.board[check_row][check_col]
                if square == friendly_pawn:
                    friendly_count += 1
                elif square == enemy_pawn:
                    enemy_count += 1

        return friendly_count >= enemy_count

    @classmethod
    def candidate_passed_pawn_value(cls, gs, row, col, color):
        if color == 'w':
            rank = 7 - row
            rank_bonus = [0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.4, 0][rank]
        else:
            rank = row
            rank_bonus = [0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.4, 0][rank]

        bonus = rank_bonus

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

        pawn_advantage = friendly_count - enemy_count
        if pawn_advantage >= 2:
            bonus *= 1.5
        elif pawn_advantage == 1:
            bonus *= 1.2

        if color == 'w' and row <= 2:
            bonus *= 1.3
        elif color == 'b' and row >= 5:
            bonus *= 1.3

        return bonus

    @staticmethod
    def evaluate_passed_pawns(gs):
        score = 0
        for row in range(8):
            for col in range(8):
                square = gs.board[row][col]
                if square == 'wp':
                    if SmartMoveFinder.is_passed_pawn(gs, row, col, 'w'):
                        bonus = SmartMoveFinder.passed_pawn_value(gs, row, col, 'w')
                        score += bonus
                    elif SmartMoveFinder.is_candidate_passed_pawn(gs, row, col, 'w'):
                        bonus = SmartMoveFinder.candidate_passed_pawn_value(gs, row, col, 'w')
                        score += bonus
                elif square == 'bp':
                    if SmartMoveFinder.is_passed_pawn(gs, row, col, 'b'):
                        bonus = SmartMoveFinder.passed_pawn_value(gs, row, col, 'b')
                        score -= bonus
                    elif SmartMoveFinder.is_candidate_passed_pawn(gs, row, col, 'b'):
                        bonus = SmartMoveFinder.candidate_passed_pawn_value(gs, row, col, 'b')
                        score -= bonus
        return score

    @staticmethod
    def scoreBoard(gs):
        if gs.checkMate:
            if gs.whiteToMove:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif gs.staleMate:
            return STALEMATE

        score = 0

        # Tempo bonus only in middlegame
        if not SmartMoveFinder.is_endgame(gs):
            score += 0.12 if gs.whiteToMove else -0.12

        # Material + Position
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    piece_type = square[1]
                    piece_color = square[0]

                    if piece_type == 'K':
                        pos_table = kingScores_eg if SmartMoveFinder.is_endgame(gs) else piecePositionScores["K"]
                    else:
                        pos_table = piecePositionScores.get(square if piece_type == 'p' else piece_type, [])

                    if piece_type == 'p':
                        position_score = pos_table[row][col]
                    else:
                        if piece_color == 'w':
                            position_score = pos_table[7 - row][col]
                        else:
                            position_score = pos_table[row][col]

                    material_score = pieceScore[piece_type]

                    if piece_color == 'w':
                        score += material_score + (position_score * 0.1)
                    elif piece_color == 'b':
                        score -= (material_score + (position_score * 0.1))

        # Castling evaluation
        if gs.board[7][6] == 'wK' and gs.board[7][5] == 'wR':
            score += 0.5
        if gs.board[7][2] == 'wK' and gs.board[7][3] == 'wR':
            score += 0.5
        if gs.board[7][4] == 'wK':
            if not gs.currentCastlingRights.wks and not gs.currentCastlingRights.wqs:
                score -= 0.35

        if gs.board[0][6] == 'bK' and gs.board[0][5] == 'bR':
            score -= 0.5
        if gs.board[0][2] == 'bK' and gs.board[0][3] == 'bR':
            score -= 0.5
        if gs.board[0][4] == 'bK':
            if not gs.currentCastlingRights.bks and not gs.currentCastlingRights.bqs:
                score += 0.35

        # Passed pawns
        score += SmartMoveFinder.evaluate_passed_pawns(gs)

        # Pawn weaknesses
        score += SmartMoveFinder.evaluate_pawn_weaknesses(gs)

        return score