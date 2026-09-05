import sys
import chess
import chess.polyglot
import threading
from ChessEngine import GameState, Move
from SmartMoveFinder import SmartMoveFinder


try:
    # NOTE: this needs an actual compiled Polyglot .bin opening book file.
    # gm-2600-m35.pgn (a plain PGN game archive) is NOT that - see the
    # comment further down for how to build one if you want an opening book.
    opening_book = chess.polyglot.open_reader("gm-2600-m35.bin")
except Exception as e:
    opening_book = None
    print(f"info string opening book unavailable: {e}", file=sys.stderr)


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


def search_and_play(think_time):
    global stop_search

    # NEW: define this up front, outside the try block. Previously it was only
    # assigned inside the try, so if anything threw before that line ran, the
    # except handler's own fallback (which reads validMoves) would hit a
    # NameError and crash with zero "bestmove" output - leaving the GUI
    # waiting forever instead of getting even a bad move.
    validMoves = []

    try:
        # 1. Update Time Limit
        # (This will crash if you didn't add set_time_limit to SmartMoveFinder)
        if hasattr(SmartMoveFinder, 'set_time_limit'):
            SmartMoveFinder.set_time_limit(think_time)
        else:
            print("info string ERROR: set_time_limit method missing in SmartMoveFinder", file=sys.stderr)

        validMoves = gs.getValidMoves()
        if not validMoves:
            print("bestmove 0000")
            sys.stdout.flush()
            return

        # 2. Run Search
        best_move = SmartMoveFinder.findBestMove(gs, validMoves)

        if opening_book:
            board = chess.Board(gs.get_fen())
            entry = opening_book.get(board)

            if entry:
                move_uci = entry.move.uci()
                print(f"bestmove {move_uci}")
                sys.stdout.flush()
                return
            best_move = SmartMoveFinder.findBestMove(gs, validMoves)

        # 3. Safety Check
        if best_move is None or best_move not in validMoves:
            print("info string ALERT: AI failed to return a valid move. Playing random.", file=sys.stderr)
            best_move = validMoves[0]

        if stop_search:
            return

        uci = move_to_uci(best_move)
        print(f"bestmove {uci}")
        sys.stdout.flush()

    except Exception as e:
        # THIS IS THE IMPORTANT PART: It prints the crash to Arena's F4 Log
        import traceback
        error_msg = traceback.format_exc().replace('\n', ' ')
        print(f"info string CRASH: {error_msg}", file=sys.stderr)

        # NEW: this fallback used to be a single line that could itself throw
        # (NameError if validMoves was never set, or an error inside
        # move_to_uci on a weird move) and take down the whole process with
        # NO "bestmove" line printed at all - the single worst outcome for a
        # UCI engine, since the GUI just hangs. Now it's wrapped so we always
        # emit *something*.
        try:
            if validMoves:
                print(f"bestmove {move_to_uci(validMoves[0])}")
            else:
                print("bestmove 0000")
        except Exception:
            print("bestmove 0000")
        sys.stdout.flush()




# In UCI.py

def handle_go(cmd):
    global search_thread, stop_search
    stop_search = False

    # 1. Parse Time from command (e.g., "go wtime 300000 btime 300000")
    tokens = cmd.split()
    time_left = None

    # Check whose turn it is
    is_white = gs.whiteToMove
    key = "wtime" if is_white else "btime"

    if key in tokens:
        idx = tokens.index(key)
        if idx + 1 < len(tokens):
            time_ms = int(tokens[idx + 1])
            time_left = time_ms / 1000.0  # Convert to seconds

    # 2. Decide how long to think
    if time_left:
        # Simple time management: use 1/30th of remaining time
        think_time = time_left / 30.0
    else:
        # Default for "infinite" analysis or fixed time
        think_time = 5.0

    # 3. Pass this time to the engine
    # (We need to update search_and_play to accept this argument)
    search_thread = threading.Thread(target=search_and_play, args=(think_time,))
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
            SmartMoveFinder.transposition_table.clear()
            SmartMoveFinder.clear_search_data()

        elif cmd.startswith("position"):
            handle_position(cmd)

        elif cmd.startswith("go"):
            handle_go(cmd)

        elif cmd == "stop":
            handle_stop()

        elif cmd == "quit":
            break


if __name__ == "__main__":
    uci_loop()