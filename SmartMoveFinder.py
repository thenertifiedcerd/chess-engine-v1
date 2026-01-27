import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0


class SmartMoveFinder:
    @staticmethod
    def findRandomMove(validMoves):
        return validMoves[random.randint(0, len(validMoves) - 1)]

    @staticmethod
    def scoreMaterial(board):
        score = 0
        for row in board:
            for square in row:
                if square[0] == 'w':
                    score += pieceScore[square[1]]
                elif square[0] == 'b':
                    score -= pieceScore[square[1]]
        return score

    @staticmethod
    def findBestMove(gs, validMoves):
        turnMultiplier = 1 if gs.whiteToMove else -1

        # We want to maximize our score, but we assume the opponent will
        # play the move that minimizes our score.
        opponentMinMaxScore = CHECKMATE
        bestPlayerMove = None
        random.shuffle(validMoves)
        random.shuffle(validMoves)

        for playerMove in validMoves:
            gs.makeMove(playerMove)  # 1. Make our move

            opponentsMoves = gs.getValidMoves()

            # If making this move ends the game immediately, check that first
            if gs.checkMate:
                opponentMaxScore = -CHECKMATE
            elif gs.staleMate:
                opponentMaxScore = STALEMATE
            else:
                # 2. Simulate Opponent's response
                opponentMaxScore = -CHECKMATE
                for oppMove in opponentsMoves:  # Rename variable to avoid shadowing
                    gs.makeMove(oppMove)  # Make opponent move

                    if gs.checkMate:
                        score = CHECKMATE
                    elif gs.staleMate:
                        score = STALEMATE
                    else:
                        # Score is usually negative for opponent, so we flip it
                        score = -turnMultiplier * SmartMoveFinder.scoreMaterial(gs.board)

                    if score > opponentMaxScore:
                        opponentMaxScore = score

                    gs.undoMove()  # CRITICAL: Undo opponent move

            # 3. If the opponent's BEST response is worse than our current best case,
            # this is a better move for us. (We want to minimize their advantage)
            if opponentMaxScore < opponentMinMaxScore:
                opponentMinMaxScore = opponentMaxScore
                bestPlayerMove = playerMove

            gs.undoMove()  # CRITICAL: Undo our move

        return bestPlayerMove