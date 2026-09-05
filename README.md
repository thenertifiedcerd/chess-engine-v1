# Chess Engine

A Python chess engine with a pygame GUI and a custom AI opponent.

---

## Features

### Game Rules
- Full legal move generation (pins, checks, checkmate, stalemate)
- Castling (kingside and queenside) for both sides
- En passant
- Pawn promotion (auto-promotes to queen)
- Insufficient material draw (two kings only)

### AI
- **Negamax with Alpha-Beta pruning**
- **Iterative deepening** — searches progressively deeper within a time limit, always returning the best fully-completed depth
- **Transposition table** — Zobrist hashing with incremental updates avoids re-evaluating repeated positions
- **Quiescence search** — extends search on captures and promotions to prevent horizon-effect blunders
- **Move ordering** — TT move first, then MVV-LVA captures, killer moves, history heuristic; ensures best moves are searched first for maximum pruning
- **Late Move Reductions (LMR)** — reduces search depth on quiet moves unlikely to be best
- **Null move pruning** — with verification search at deep nodes
- **Check extensions** — extends search depth when in check so tactics aren't missed
- **Piece-square tables** — separate middlegame and endgame tables for all piece types including king
- **Passed pawn evaluation** — bonuses for advanced passed pawns, connected passers, and candidate passers
- **Pawn weakness detection** — penalises doubled, isolated, and backward pawns

### Engine Infrastructure
- Incremental Zobrist hashing on every make/undo move
- AI runs on a cloned game state — search never touches the real board
- Sandboxed move matching — AI moves are validated against the real legal move list before being played

---

## Estimated Playing Strength

**~1400–1600 ELO**

| Engine | ELO |
|---|---|
| Random mover | ~200 |
| Minimax depth 2 | ~600 |
| **This engine** | **~1400–1600** |
| Amateur club player | ~1500 |
| Stockfish level 1 | ~1350 |
| Sunfish (Python) | ~1500–1800 |
| Stockfish (full strength) | ~3500 |

---

## Known Limitations / Planned Improvements

### Correctness
- [ ] **Threefold repetition draw** — the Zobrist hash log is already in place; detection would take ~10 lines
- [ ] **50-move rule** — no half-move clock is tracked

### Search Performance
- [ ] **Faster attack detection** — `squareUnderAttack` currently generates all pseudo-legal opponent moves (O(n)); replacing it with per-piece lookup tables (pawn, knight, king) and ray casting (rook, bishop, queen) would be 10–20× faster and allow 1–2 extra plies at the same time control
- [ ] **`getValidMoves` called at every node** — the inner search loop calls this on every position, each of which internally calls `makeMove`/`undoMove` per candidate; a staged move generator would reduce this overhead significantly
- [ ] **Aspiration windows** — narrowing the alpha-beta window around the previous iteration's score would reduce nodes searched during iterative deepening
- [ ] **No bitboard representation** — the 2D string-array board is the primary speed ceiling for a Python engine; a bitboard approach would allow bulk operations on piece sets

### Evaluation
- [ ] **King safety** — no pawn shield evaluation, no penalty for open files near the king; this is the single biggest evaluation gap in the middlegame
- [ ] **Rook on open/semi-open file** — standard positional bonus missing
- [ ] **Bishop pair bonus** — two bishops in open positions are stronger than bishop + knight
- [ ] **Mobility scoring** — rewarding pieces with more available squares encourages active play
- [ ] **Contempt factor** — the engine currently scores stalemate as 0 in all situations; a small contempt value would make it avoid stalemate when winning and prefer it when losing

---

## Controls

| Input | Action |
|---|---|
| Click piece → click square | Make a move |
| `X` | Undo last move |
| `R` | Reset board |

---

## Project Structure

```
ChessEngine.py        # Board state, move generation, make/undo, Zobrist hashing
SmartMoveFinder.py    # AI search (negamax, alpha-beta, evaluation)
ChessMain.py          # pygame GUI and game loop
UCI.py                # UCI protocol adapter
images/               # Piece images
```

---

## Requirements

```
pygame
```

```bash
pip install pygame
python ChessMain.py
```
