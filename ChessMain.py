import pygame as p
import ChessEngine
from ChessEngine import GameState, SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8 by 8 chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for later animation
IMAGES = {}


def loadImages():
    pieces = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wp', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False
    playerOne = True # If True, human plays White. If False, AI plays White.
    playerTwo = False # If True, human plays Black. If False, AI plays Black.

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if row >= DIMENSION or col >= DIMENSION: continue  # Safety check for clicks outside board

                    piece = gs.board[row][col]
                    if piece != "--" and (
                            (piece[0] == 'w' and gs.whiteToMove) or (piece[0] == 'b' and not gs.whiteToMove)):
                        if sqSelected == (row, col):  # user clicked the same square twice
                            sqSelected = ()  # deselect
                            playerClicks = []  # clear player clicks
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    else:
                        if sqSelected:
                            playerClicks.append((row, col))

                    if len(playerClicks) == 2:  # after 2nd click
                        startSq, endSq = playerClicks[0], playerClicks[1]
                        # Match by start/end square only so that special moves
                        # (castling, en passant) are recognised correctly —
                        # the player just clicks the squares; the valid-move
                        # object already carries the correct flags.
                        # For pawn promotion, prefer queen (first match wins).
                        matched_move = None
                        for vm in validMoves:
                            if (vm.startRow, vm.startCol) == startSq and \
                               (vm.endRow,   vm.endCol)   == endSq:
                                matched_move = vm
                                break
                        if matched_move is not None:
                            gs.makeMove(matched_move)
                            animateMove(matched_move, screen, gs.board, clock)
                            moveMade = True
                            print("Human:", matched_move.getChessNotation())
                            sqSelected = ()
                            playerClicks = []
                            validMoves = gs.getValidMoves()
                        else:
                            print('Invalid move: ', startSq, '->', endSq)
                            playerClicks = [sqSelected]

            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_x:  # 'x' key to undo move
                    gs.undoMove()
                    moveMade = True
                    gameOver = False  # Undo allows playing again
                if e.key == p.K_r:  # resets board when pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

         # --- AI MOVE FINDER LOGIC ---
        # Re-evaluate humanTurn here so that moves made earlier in this same
        # frame (e.g. an undo key) are reflected before we decide to let the AI play.
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        if not gameOver and not humanTurn and not moveMade:
            # 1. Create an isolated sandbox copy of the board for the AI
            ai_sandbox_gs = gs.clone()
            sandbox_valid_moves = ai_sandbox_gs.getValidMoves()

            # 2. Pass the sandbox into the search tree so it leaves the real board completely untouched
            AIMove = SmartMoveFinder.findBestMove(ai_sandbox_gs, sandbox_valid_moves)

            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)

            if AIMove:
                # 3. Match the AI's move to a legal move on the real board.
                # Never use the fallback Move() constructor — it bypasses legality
                # checks and could produce an illegal or king-capturing move.
                real_move_to_execute = None
                for move in validMoves:
                    if move == AIMove:
                        real_move_to_execute = move
                        break

                if real_move_to_execute is not None:
                    print("AI thinking complete → playing:", real_move_to_execute.getChessNotation())
                    gs.makeMove(real_move_to_execute)
                    animateMove(real_move_to_execute, screen, gs.board, clock)
                    print("AI:", real_move_to_execute.getChessNotation())
                    validMoves = gs.getValidMoves()
                    moveMade = True
                else:
                    # AIMove came from the sandbox but doesn't exist in the real
                    # valid-moves list — this should not happen, but if it does
                    # we must not play it.  Log and fall through gracefully.
                    print("AI returned a move not found in real validMoves — skipping:",
                          AIMove.getChessNotation())
            else:
                if gs.checkMate or gs.staleMate:
                    gameOver = True

            # Flush any clicks queued while the AI was thinking
            p.event.clear()

        # Update valid moves after AI plays or Undo
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        # --- DRAW CURRENT STABLE GAME STATE ---
        # Moving this strictly below the AI processing ensures that the board rendering
        # only captures finalized moves, entirely hiding the search mutations.
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate.")
            else:
                drawText(screen, "White wins by checkmate.")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate, game over.")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    colors = [p.Color("#f1d9b4"), p.Color("#b48963")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('#9bc70069'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('#C3FA00'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    colors = [p.Color("#f1d9b4"), p.Color("#b48963")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    framesCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(framesCount + 1):
        r, c = (move.startRow + dR * frame / framesCount, move.startCol + dC * frame / framesCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont('Arial', 32, bold=True)
    textObject = font.render(text, True, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2 + 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2 + 2)
    screen.blit(textObject, textLocation)

    textObject = font.render(text, True, p.Color('Red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()