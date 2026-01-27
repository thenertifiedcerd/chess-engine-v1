# Simple Stockfish UCI adapter for chess-engine-v1 (no external deps).
# Usage: instantiate StockfishAdapter(path='stockfish'), start(), configure(...),
# new_game(), set_position_from_gs(gs), go(movetime=1000) -> returns UCI string like 'e2e4'.

import subprocess
import threading
import queue
import time
import shlex

FILES = 'abcdefgh'

class StockfishAdapter:
    def __init__(self, path='stockfish'):
        self.path = path
        self.proc = None
        self.q = queue.Queue()
        self.thread = None

    def start(self):
        if self.proc:
            return
        # Start stockfish process (must be on PATH or provide absolute path)
        self.proc = subprocess.Popen([self.path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        # handshake
        self._send('uci')
        self._wait_for_token('uciok', timeout=5.0)

    def _reader(self):
        for line in self.proc.stdout:
            self.q.put(line.rstrip('\n'))
        # signal end
        self.q.put(None)

    def _send(self, cmd):
        if not self.proc:
            raise RuntimeError('Engine not started')
        self.proc.stdin.write(cmd + '\n')
        self.proc.stdin.flush()

    def _wait_for_token(self, token, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = self.q.get(timeout=deadline - time.time())
            except queue.Empty:
                break
            if line is None:
                break
            if line.strip() == token:
                return True
        return False

    def is_ready(self, timeout=5.0):
        self._send('isready')
        return self._wait_for_token('readyok', timeout=timeout)

    def configure(self, options: dict):
        # options is a dict: {'UCI_LimitStrength': 'true', 'UCI_Elo': '1500', 'Threads': '2', 'Hash': '64'}
        for name, value in options.items():
            # value must be a string (or convertible)
            self._send(f'setoption name {name} value {value}')
        self.is_ready()

    def new_game(self):
        self._send('ucinewgame')
        self.is_ready()

    def stop(self):
        if not self.proc:
            return
        try:
            self._send('quit')
        except Exception:
            pass
        self.proc = None

    def _move_to_uci(self, move):
        # move is ChessEngine.Move instance with startRow, startCol, endRow, endCol
        sf = FILES[move.startCol]
        sr = str(8 - move.startRow)
        ef = FILES[move.endCol]
        er = str(8 - move.endRow)
        u = f'{sf}{sr}{ef}{er}'
        # handle promotion if the Move object indicates pawn promotion via its flags or piece types
        # For safety, if the moving piece was a pawn and it reached last rank, append promotion letter if present
        try:
            # Some Move implementations set promotedPiece or similar; try sensible fallbacks
            promoted = getattr(move, 'promotion', None) or getattr(move, 'promotedTo', None) or getattr(move, 'promoted', None)
            if promoted:
                # convert to lowercase UCI promotion letter
                u += promoted.lower()
            else:
                # if move is pawn and moved to last rank, infer promotion from piece on board (if present)
                # This inference is optional; Stockfish's responses will include promotion letter already.
                pass
        except Exception:
            pass
        return u

    def set_position_from_gs(self, gs):
        # gs is an instance of ChessEngine.GameState
        # Build moves list from gs.moveLog
        u_moves = []
        for mv in gs.moveLog:
            # convert each stored Move -> uci
            u_moves.append(self._move_to_uci(mv))
        if u_moves:
            cmd = 'position startpos moves ' + ' '.join(u_moves)
        else:
            cmd = 'position startpos'
        self._send(cmd)

    def go(self, movetime=None, depth=None, nodes=None, timeout=10.0):
        # non-blocking search parameters: specify one of movetime (ms), depth (ply), nodes
        if movetime is not None:
            self._send(f'go movetime {int(movetime)}')
        elif depth is not None:
            self._send(f'go depth {int(depth)}')
        elif nodes is not None:
            self._send(f'go nodes {int(nodes)}')
        else:
            self._send('go movetime 1000')  # default 1s

        # wait for bestmove line
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = self.q.get(timeout=deadline - time.time())
            except queue.Empty:
                break
            if line is None:
                break
            line = line.strip()
            # example: "bestmove e2e4 ponder e7e5"
            if line.startswith('bestmove'):
                parts = shlex.split(line)
                if len(parts) >= 2:
                    return parts[1]
                return None
        return None