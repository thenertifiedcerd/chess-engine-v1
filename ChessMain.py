import pygame as p
import ChessEngine
from ChessEngine import GameState, SmartMoveFinder

# --- OPTIONAL: Import your Stockfish Adapter if you saved it in a file ---
# from StockfishAdapter import StockfishAdapter 

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
    playerOne = False # If True, human plays White. If False, AI plays White.
    playerTwo = False # If True, human plays Black. If False, AI plays Black.

    # --- STOCKFISH SETUP (Uncomment if using the adapter) ---
    # stockfish = StockfishAdapter(path="stockfish.exe") # Make sure path is correct
    # stockfish.start()
    # --------------------------------------------------------

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                # if 'stockfish' in locals(): stockfish.stop() # Cleanup stockfish

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
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # only print and execute if move is valid for the side to move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                animateMove(validMoves[i], screen, gs.board, clock)
                                moveMade = True
                                animate = True
                                print("Human:", move.getChessNotation())

                                # clear selection after a successful move
                                sqSelected = ()
                                playerClicks = []

                                # --- CRITICAL FIX: Update moves IMMEDIATELY for the AI ---
                                # This ensures the AI sees the new board state right away
                                validMoves = gs.getValidMoves()
                                # ---------------------------------------------------------
                                break
                        if not moveMade:
                            print('Invalid move:', move.getChessNotation())
                            playerClicks = [sqSelected]

            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_x:  # 'x' key to undo move
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False  # Undo allows playing again
                if e.key == p.K_r:  # resets board when pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # --- AI MOVE FINDER LOGIC ---
        if not gameOver and not humanTurn and not moveMade:
            # OPTION 1: Random Mover (Currently Active)
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            # OPTION 2: Stockfish (Uncomment to use)
            # stockfish.set_position_from_gs(gs)
            # uci_move = stockfish.go(movetime=1000)
            # if uci_move:
            #     # You need a helper to convert UCI string back to Move object here
            #     # For now, we stick to random to prevent crashes without the converter
            #     pass

            if AIMove is None:
                # If validMoves is empty, check why
                if gs.checkMate or gs.staleMate:
                    gameOver = True
                else:
                    # Retry generating moves if something glitched
                    validMoves = gs.getValidMoves()
            else:
                gs.makeMove(AIMove)
                animateMove(AIMove, screen, gs.board, clock)
                moveMade = True
                animate = True
                print("AI:", AIMove.getChessNotation())

        # Update valid moves after AI plays or Undo
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

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
        # Only highlight if the selected piece belongs to the turn owner
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('#9bc70069'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('#C3FA00'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    colors = [p.Color("#f1d9b4"), p.Color("#b48963")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5  # frames to move one square
    framesCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(framesCount + 1):
        r, c = (move.startRow + dR * frame / framesCount, move.startCol + dC * frame / framesCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square (board already has move applied)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle if there was one
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont('Arial', 32, bold=True)
    textObject = font.render(text, True, p.Color('Black'))  # Shadow
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2 + 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2 + 2)
    screen.blit(textObject, textLocation)

    textObject = font.render(text, True, p.Color('Red'))  # Main Text
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()