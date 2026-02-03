import sys
import threading
from ChessEngine import GameState, Move
from SmartMoveFinder import SmartMoveFinder

# Global engine state
gs = GameState()
search_thread = None
stop_search = False


# -----------------------------
# Utility: UCI move ↔ Move
# -----------------------------

def move_to_uci(move):
    s = (
        Move.colsToFiles[move.startCol] +
        Move.rowsToRanks[move.startRow] +
        Move.colsToFiles[move.endCol] +
        Move.rowsToRanks[move.endRow]
    )
    if move.isPawnPromotion:
        s += move.promotedPiece.lower()
    return s


def parse_uci_move(gs, uci):
    start_col = Move.filesToCols[uci[0]]
    start_row = Move.ranksToRows[uci[1]]
    end_col = Move.filesToCols[uci[2]]
    end_row = Move.ranksToRows[uci[3]]
    promo = uci[4].upper() if len(uci) == 5 else None

    for move in gs.getValidMoves():
        if (move.startRow == start_row and
            move.startCol == start_col and
            move.endRow == end_row and
            move.endCol == end_col):

            if move.isPawnPromotion and promo:
                move.promotedPiece = promo
            return move
    return None


# -----------------------------
# FEN Loader
# -----------------------------

def load_fen(gs, fen):
    parts = fen.split()
    board_part, turn, castling, ep = parts[:4]

    gs.board = [["--"] * 8 for _ in range(8)]
    rows = board_part.split("/")

    for r in range(8):
        c = 0
        for ch in rows[r]:
            if ch.isdigit():
                c += int(ch)
            else:
                color = 'w' if ch.isupper() else 'b'
                piece = ch.upper()
                if piece == 'P':
                    piece = 'p'
                gs.board[r][c] = color + piece
                if piece == 'K':
                    if color == 'w':
                        gs.whiteKingPosition = (r, c)
                    else:
                        gs.blackKingPosition = (r, c)
                c += 1

    gs.whiteToMove = (turn == 'w')

    gs.currentCastlingRights.wks = 'K' in castling
    gs.currentCastlingRights.wqs = 'Q' in castling
    gs.currentCastlingRights.bks = 'k' in castling
    gs.currentCastlingRights.bqs = 'q' in castling

    gs.enPassantPossible = ()
    if ep != '-':
        col = Move.filesToCols[ep[0]]
        row = Move.ranksToRows[ep[1]]
        gs.enPassantPossible = (row, col)

    gs.moveLog = []
    gs.current_zobrist_hash = gs.generate_initial_hash()
    gs.zobrist_log = [gs.current_zobrist_hash]


# -----------------------------
# UCI Command Handlers
# -----------------------------

def handle_position(cmd):
    tokens = cmd.split()

    if tokens[1] == "startpos":
        gs.__init__()
        idx = 2
    else:
        fen = " ".join(tokens[2:8])
        load_fen(gs, fen)
        idx = 8

    if idx < len(tokens) and tokens[idx] == "moves":
        for uci_move in tokens[idx + 1:]:
            move = parse_uci_move(gs, uci_move)
            if move:
                gs.makeMove(move)


def search_and_play():
    global stop_search

    valid_moves = gs.getValidMoves()
    if not valid_moves:
        print("bestmove 0000")
        sys.stdout.flush()
        return

    best_move = SmartMoveFinder.findBestMove(gs, valid_moves)

    if stop_search:
        return

    uci = move_to_uci(best_move)
    print(f"bestmove {uci}")
    sys.stdout.flush()


def handle_go():
    global search_thread, stop_search
    stop_search = False

    search_thread = threading.Thread(target=search_and_play)
    search_thread.start()


def handle_stop():
    global stop_search
    stop_search = True


# -----------------------------
# Main UCI Loop
# -----------------------------

def uci_loop():
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        cmd = line.strip()

        if cmd == "uci":
            print("id name PythonChessEngine")
            print("id author You")
            print("uciok")
            sys.stdout.flush()

        elif cmd == "isready":
            print("readyok")
            sys.stdout.flush()

        elif cmd == "ucinewgame":
            gs.__init__()

        elif cmd.startswith("position"):
            handle_position(cmd)

        elif cmd.startswith("go"):
            handle_go()

        elif cmd == "stop":
            handle_stop()

        elif cmd == "quit":
            break


if __name__ == "__main__":
    uci_loop()
